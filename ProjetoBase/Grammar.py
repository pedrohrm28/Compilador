from Consts import Consts
from SemanticVisitor import *
from Error import Error

class Grammar:
    def __init__(self, parser):
        self.parser = parser
    def Rule(self):
        return self.GetParserManager().fail(f"{Error.parserError}: Implementar suas regras de producao (Heranca de Grammar)!")
    def CurrentToken(self): return self.parser.CurrentTok()
    def NextToken(self): return self.parser.NextTok()
    def GetParserManager(self): return self.parser.Manager()

    @staticmethod
    def StartSymbol(parser):
        ast = parser.Manager()
        node = ast.registry(Exp(parser).Rule())
        if ast.error: return ast
        if parser.CurrentTok().type != Consts.EOF:
            return ast.fail(f"{Error.parserError}: Esperava fim de entrada, encontrei {parser.CurrentTok()}")
        return ast.success(node)

##############################
# Exp ::= [LET] ID EQ Exp | ID EQ Exp | Sum
class Exp(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        tok = self.CurrentToken()

        if tok.matches(Consts.KEY, Consts.LET):
            self.NextToken()
            if self.CurrentToken().type != Consts.ID:
                return ast.fail(f"{Error.parserError}: Esperado identificador apos 'let'")
            varTok = self.CurrentToken(); self.NextToken()
            if self.CurrentToken().type != Consts.EQ:
                return ast.fail(f"{Error.parserError}: Esperado '=' apos identificador")
            self.NextToken()
            expr = ast.registry(Exp(self.parser).Rule())
            if ast.error: return ast
            return ast.success(NoVarAssign(varTok, expr))

        if tok.type == Consts.ID and self.parser.Lookahead(1).type == Consts.EQ:
            varTok = tok; self.NextToken(); self.NextToken()
            expr = ast.registry(Exp(self.parser).Rule())
            if ast.error: return ast
            return ast.success(NoVarAssign(varTok, expr))

        return Sum(self.parser).Rule()

##############################
# Sum / Product / Unary / Pow
class Sum(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        left = ast.registry(Product(self.parser).Rule())
        if ast.error: return ast
        while self.CurrentToken().type in (Consts.PLUS, Consts.MINUS):
            opTok = self.CurrentToken(); self.NextToken()
            right = ast.registry(Product(self.parser).Rule())
            if ast.error: return ast
            left = NoOpBinaria(left, opTok, right)
        return ast.success(left)

class Product(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        left = ast.registry(Unary(self.parser).Rule())
        if ast.error: return ast
        while self.CurrentToken().type in (Consts.MUL, Consts.DIV):
            opTok = self.CurrentToken(); self.NextToken()
            right = ast.registry(Unary(self.parser).Rule())
            if ast.error: return ast
            left = NoOpBinaria(left, opTok, right)
        return ast.success(left)

class Unary(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        ops = []
        while self.CurrentToken().type in (Consts.PLUS, Consts.MINUS):
            ops.append(self.CurrentToken()); self.NextToken()
        node = ast.registry(Pow(self.parser).Rule())
        if ast.error: return ast
        for opTok in reversed(ops):
            node = NoUnary(opTok, node)
        return ast.success(node)

class Pow(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        left = ast.registry(Primary(self.parser).Rule())
        if ast.error: return ast
        if self.CurrentToken().type == Consts.POW:
            opTok = self.CurrentToken(); self.NextToken()
            right = ast.registry(Unary(self.parser).Rule())
            if ast.error: return ast
            left = NoOpBinaria(left, opTok, right)
        return ast.success(left)

##############################
# Primary ::= Atom Suffix*
# Suffix  ::= CallSuffix | MemberSuffix
class Primary(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        node = ast.registry(Atom(self.parser).Rule())
        if ast.error: return ast
        while True:
            tok = self.CurrentToken()
            if tok.type == Consts.LPAR:
                node = self._parse_call_suffix(node)
                continue
            if tok.type == Consts.DOT:
                node = self._parse_member_suffix(node)
                continue
            break
        return ast.success(node)

    def _parse_call_suffix(self, calleeNode):
        ast = self.GetParserManager()
        self.NextToken()  # '('
        args = []
        if self.CurrentToken().type != Consts.RPAR:
            args.append(ast.registry(Exp(self.parser).Rule()))
            if ast.error: return ast
            while self.CurrentToken().type == Consts.COMMA:
                self.NextToken()
                args.append(ast.registry(Exp(self.parser).Rule()))
                if ast.error: return ast
        if self.CurrentToken().type != Consts.RPAR:
            return ast.fail(f"{Error.parserError}: Esperado ')'")
        self.NextToken()
        return NoCall(calleeNode, args)

    def _parse_member_suffix(self, objNode):
        ast = self.GetParserManager()
        if self.CurrentToken().type != Consts.DOT:
            return ast.fail(f"{Error.parserError}: Esperado '.' para acesso a membro")
        self.NextToken()
        if self.CurrentToken().type != Consts.ID:
            return ast.fail(f"{Error.parserError}: Esperado identificador apos '.'")
        nameTok = self.CurrentToken(); self.NextToken()
        return NoMemberAccess(objNode, nameTok)

##############################
# Atom
class Atom(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        tok = self.CurrentToken()

        if tok.matches(Consts.KEY, Consts.FUNC):
            self.NextToken()
            if self.CurrentToken().type != Consts.LPAR:
                return ast.fail(f"{Error.parserError}: Esperado '(' apos 'fn'")
            self.NextToken()
            params = []
            if self.CurrentToken().type != Consts.RPAR:
                if self.CurrentToken().type != Consts.ID:
                    return ast.fail(f"{Error.parserError}: Esperado identificador de parametro")
                params.append(self.CurrentToken().value); self.NextToken()
                while self.CurrentToken().type == Consts.COMMA:
                    self.NextToken()
                    if self.CurrentToken().type != Consts.ID:
                        return ast.fail(f"{Error.parserError}: Esperado identificador de parametro")
                    params.append(self.CurrentToken().value); self.NextToken()
            if self.CurrentToken().type != Consts.RPAR:
                return ast.fail(f"{Error.parserError}: Esperado ')'")
            self.NextToken()
            if self.CurrentToken().type != Consts.ARROW:
                return ast.fail(f"{Error.parserError}: Esperado '->' apos parametros")
            self.NextToken()
            body = ast.registry(Exp(self.parser).Rule())
            if ast.error: return ast
            return ast.success(NoFuncLiteral(params, body))

        # Parênteses ou tupla
        if tok.type == Consts.LPAR:
            if self._is_tuple_start(): return TupleExp(self.parser).Rule()
            self.NextToken()
            node = ast.registry(Exp(self.parser).Rule())
            if ast.error: return ast
            if self.CurrentToken().type != Consts.RPAR:
                return ast.fail(f"{Error.parserError}: Esperado ')'")
            self.NextToken()
            return ast.success(node)

        # Lista
        if tok.type == Consts.LSQUARE:
            return ListExp(self.parser).Rule()

        # Objeto literal
        if tok.type == Consts.LBRACE:
            return ObjectExp(self.parser).Rule()

        # Literais simples
        if tok.type in (Consts.INT, Consts.FLOAT):
            self.NextToken(); return ast.success(NoNumber(tok))
        if tok.type == Consts.STRING:
            self.NextToken(); return ast.success(NoString(tok))
        if tok.type == Consts.ID:
            self.NextToken(); return ast.success(NoVarAccess(tok))

        return ast.fail(f"{Error.parserError}: Token inesperado em Atom: {tok}")

    def _is_tuple_start(self):
        depth, i = 0, 0
        while True:
            tok = self.parser.Lookahead(i)
            if tok.type == Consts.LPAR: depth += 1
            elif tok.type == Consts.RPAR:
                depth -= 1
                if depth == 0: return False
            elif tok.type == Consts.COMMA and depth == 1:
                return True
            elif tok.type == Consts.EOF: return False
            i += 1

##############################
# ListExp ::= [ Exp ( , Exp )* ]
class ListExp(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        if self.CurrentToken().type != Consts.LSQUARE:
            return ast.fail(f"{Error.parserError}: Esperado '[' para lista")
        self.NextToken()
        elements = []
        if self.CurrentToken().type != Consts.RSQUARE:
            elements.append(ast.registry(Exp(self.parser).Rule()))
            if ast.error: return ast
            while self.CurrentToken().type == Consts.COMMA:
                self.NextToken()
                elements.append(ast.registry(Exp(self.parser).Rule()))
                if ast.error: return ast
        if self.CurrentToken().type != Consts.RSQUARE:
            return ast.fail(f"{Error.parserError}: Esperado ']'")
        self.NextToken()
        return ast.success(NoList(elements))

##############################
# TupleExp ::= ( Exp ( , Exp )+ )
class TupleExp(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        if self.CurrentToken().type != Consts.LPAR:
            return ast.fail(f"{Error.parserError}: Esperado '(' para tupla")
        self.NextToken()
        elems = [ast.registry(Exp(self.parser).Rule())]
        if ast.error: return ast
        if self.CurrentToken().type != Consts.COMMA:
            return ast.fail(f"{Error.parserError}: Esperando por ',' em tupla")
        while self.CurrentToken().type == Consts.COMMA:
            self.NextToken()
            elems.append(ast.registry(Exp(self.parser).Rule()))
            if ast.error: return ast
        if self.CurrentToken().type != Consts.RPAR:
            return ast.fail(f"{Error.parserError}: Esperando por ')' em tupla")
        self.NextToken()
        return ast.success(NoTuple(elems))

##############################
# ObjectExp ::= { [ (ID | STRING) : Exp ( , (ID | STRING) : Exp )* ] }
class ObjectExp(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        if self.CurrentToken().type != Consts.LBRACE:
            return ast.fail(f"{Error.parserError}: Esperado '{{' para objeto))")
        self.NextToken()
        pairs = []
        if self.CurrentToken().type != Consts.RBRACE:
            k_tok = self.CurrentToken()
            if k_tok.type not in (Consts.ID, Consts.STRING):
                return ast.fail(f"{Error.parserError}: Esperado chave ID ou STRING no objeto")
            self.NextToken()
            if self.CurrentToken().type != Consts.COLON:
                return ast.fail(f"{Error.parserError}: Esperado ':' apos chave no objeto")
            self.NextToken()
            v = ast.registry(Exp(self.parser).Rule())
            if ast.error: return ast
            pairs.append((k_tok, v))
            while self.CurrentToken().type == Consts.COMMA:
                self.NextToken()
                k_tok = self.CurrentToken()
                if k_tok.type not in (Consts.ID, Consts.STRING):
                    return ast.fail(f"{Error.parserError}: Esperado chave ID ou STRING no objeto")
                self.NextToken()
                if self.CurrentToken().type != Consts.COLON:
                    return ast.fail(f"{Error.parserError}: Esperado ':' apos chave no objeto")
                self.NextToken()
                v = ast.registry(Exp(self.parser).Rule())
                if ast.error: return ast
                pairs.append((k_tok, v))
        if self.CurrentToken().type != Consts.RBRACE:
            return ast.fail(f"{Error.parserError}: Esperado '}}' no objeto")
        self.NextToken()
        return ast.success(NoObject(pairs))
