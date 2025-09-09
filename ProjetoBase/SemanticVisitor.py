from Error import Error
import abc
from TValue import *
from Consts import Consts
from Memory import MemoryManager

class Visitor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def visit(self, operator): 
        operator.fail(Error(f"{Error.runTimeError}: Nenhum visit para a classe '{Error.classNameOf(self)}' foi definido!"))

##############################
class NoNumber(Visitor):
    def __init__(self, tok): self.tok = tok
    def visit(self, operator):
        return operator.success(TNumber(self.tok.value).setMemory(operator))
    def __repr__(self): return f"{self.tok}"

class NoString(Visitor):
    def __init__(self, tok): self.tok = tok
    def visit(self, operator):
        return operator.success(TString(self.tok.value).setMemory(operator))
    def __repr__(self): return f"{self.tok}"

class NoUnary(Visitor):
    def __init__(self, opTok, node):
        self.opTok, self.node = opTok, node
    def visit(self, operator):
        v = operator.registry(self.node.visit(operator))
        if operator.error: return operator
        if self.opTok.type == Consts.PLUS:
            return operator.success(v.copy())
        if isinstance(v, TNumber):
            return operator.success(TNumber(-v.value).setMemory(operator))
        return operator.fail(Error(f"{Error.runTimeError}: Operador unario '-' nao suportado para {Error.classNameOf(v)}"))
    def __repr__(self): return f"({self.opTok}, {self.node})"

class NoOpBinaria(Visitor):
    def __init__(self, leftNode, opTok, rightNode):
        self.noEsq, self.opTok, self.noDir = leftNode, opTok, rightNode
    def __repr__(self): return f"({self.noEsq}, {self.opTok}, {self.noDir})"
    def visit(self, operator):
        esq = operator.registry(self.noEsq.visit(operator));  0
        if operator.error: return operator
        dir = operator.registry(self.noDir.visit(operator))
        if operator.error: return operator
        if self.opTok.type == Consts.PLUS:  res, err = esq.add(dir)
        elif self.opTok.type == Consts.MINUS: res, err = esq.sub(dir)
        elif self.opTok.type == Consts.MUL:   res, err = esq.mult(dir)
        elif self.opTok.type == Consts.DIV:   res, err = esq.div(dir)
        elif self.opTok.type == Consts.POW:   res, err = esq.pow(dir)
        else: return operator.fail(Error(f"{Error.runTimeError}: Operador desconhecido '{self.opTok.type}'"))
        if err: return operator.fail(err)
        return operator.success(res)

##############################
class NoVarAssign(Visitor):
    def __init__(self, varNameTok, valueNode):
        self.varNameTok, self.valueNode = varNameTok, valueNode
    def visit(self, operator):
        val = operator.registry(self.valueNode.visit(operator))
        if operator.error: return operator
        operator.set(self.varNameTok.value, val)
        return operator.success(val)
    def __repr__(self): return f"({self.varNameTok}, {self.valueNode})"

class NoVarAccess(Visitor):
    def __init__(self, varNameTok): self.varNameTok = varNameTok
    def visit(self, operator):
        varName = self.varNameTok.value
        value = operator.get(varName)
        if value is None: 
            return operator.fail(Error(f"{Error.runTimeError}: '{varName}' nao esta definido"))
        return operator.success(value.copy())
    def __repr__(self): return f"({self.varNameTok})"

##############################
class NoList(Visitor):
    def __init__(self, elements): self.elements = elements
    def visit(self, operator):
        lValue = []
        for element_node in self.elements:
            lValue.append(operator.registry(element_node.visit(operator)))
            if operator.error: return operator
        return operator.success(TList(lValue).setMemory(operator))
    def __repr__(self): return f"{self.elements}"

class NoTuple(Visitor):
    def __init__(self, elements): self.elements = elements
    def visit(self, operator):
        lValue = []
        for element_node in self.elements:
            lValue.append(operator.registry(element_node.visit(operator)))
            if operator.error: return operator
        return operator.success(TTuple(lValue).setMemory(operator))
    def __repr__(self): return f"{self.elements}"

##############################
# Objetos
class NoObject(Visitor):
    def __init__(self, pairs):  # pairs = [(keyTok, valueNode), ...]
        self.pairs = pairs
    def visit(self, operator):
        out = {}
        for k_tok, v_node in self.pairs:
            v = operator.registry(v_node.visit(operator))
            if operator.error: return operator
            key = k_tok.value
            out[key] = v
        return operator.success(TObject(out).setMemory(operator))
    def __repr__(self):
        return f"{{{', '.join([f'{k.value}: ...' for k,_ in self.pairs])}}}"

class NoMemberAccess(Visitor):
    def __init__(self, objNode, nameTok):
        self.objNode, self.nameTok = objNode, nameTok
    def visit(self, operator):
        obj = operator.registry(self.objNode.visit(operator))
        if operator.error: return operator
        if not isinstance(obj, TObject):
            return operator.fail(Error(f"{Error.runTimeError}: acesso a membro em tipo nao-objeto"))
        name = self.nameTok.value
        if name not in obj.value:
            return operator.fail(Error(f"{Error.runTimeError}: chave '{name}' nao existe no objeto"))
        return operator.success(obj.value[name].copy())
    def __repr__(self): return f"({self.objNode}.{self.nameTok.value})"

##############################
# Funções
class NoFuncLiteral(Visitor):
    def __init__(self, params, bodyNode):
        self.params, self.body = params, bodyNode
    def visit(self, operator):
        closure = operator.snapshot_env()
        fn = TFunction(self.params, self.body, closure).setMemory(operator)
        return operator.success(fn)
    def __repr__(self): return f"<fn({', '.join(self.params)}) -> {self.body}>"

class NoCall(Visitor):
    def __init__(self, calleeNode, argNodes):
        self.calleeNode, self.argNodes = calleeNode, argNodes
    def visit(self, operator):
        callee = operator.registry(self.calleeNode.visit(operator))
        if operator.error: return operator

        # Built-in?
        if isinstance(callee, TBuiltin):
            args = []
            for n in self.argNodes:
                args.append(operator.registry(n.visit(operator)))
                if operator.error: return operator
            res, err = callee.apply(operator, args)
            if err: return operator.fail(err)
            return operator.success(res)

        # Função do usuário
        if not isinstance(callee, TFunction):
            return operator.fail(Error(f"{Error.runTimeError}: Tentativa de chamar algo que nao e funcao"))
        args = []
        for n in self.argNodes:
            args.append(operator.registry(n.visit(operator)))
            if operator.error: return operator
        if len(args) != len(callee.params):
            return operator.fail(Error(f"{Error.runTimeError}: Aridade invalida: esperados {len(callee.params)} arg(s), recebidos {len(args)}"))
        operator.push_scope(callee.closure)
        for name, val in zip(callee.params, args):
            operator.set(name, val)
        result = operator.registry(callee.body.visit(operator))
        operator.pop_scope()
        return operator.success(result)
    def __repr__(self): return f"call({self.calleeNode}, {self.argNodes})"
