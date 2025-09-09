from Consts import Consts
from SemanticVisitor import *
from Error import Error

class Grammar:
    def __init__(self, parser):
        self.parser = parser
    def Rule(self):
        return self.GetParserManager().fail(f"{Error.parserError}: Implementar suas regras de producao (Heranca de Grammar)!")
    
    def CurrentToken(self):
        return self.parser.CurrentTok()
    
    def NextToken(self):
        return self.parser.NextTok()
    
    def GetParserManager(self):
        return self.parser.Manager()

    ##############################
    @staticmethod
    def StartSymbol(parser):
        # <Exp> EOF
        ast = parser.Manager()
        node = ast.registry(Exp(parser).Rule())
        if ast.error: return ast
        if parser.CurrentTok().type != Consts.EOF:
            return ast.fail(f"{Error.parserError}: Esperava fim de entrada, encontrei {parser.CurrentTok()}")
        return ast.success(node)
    ##############################

##############################
# Exp ::= [LET] ID EQ Exp | Term ((+|-) Term)*
class Exp(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        tok = self.CurrentToken()
        # let assignment
        if tok.matches(Consts.KEY, Consts.LET):
            self.NextToken()  
            if self.CurrentToken().type != Consts.ID:
                return ast.fail(f"{Error.parserError}: Esperado identificador apos 'let'")
            varTok = self.CurrentToken()
            self.NextToken()
            if self.CurrentToken().type != Consts.EQ:
                return ast.fail(f"{Error.parserError}: Esperado '=' apos identificador")
            self.NextToken()  # '='
            expr = ast.registry(Exp(self.parser).Rule())
            if ast.error: return ast
            return ast.success(NoVarAssign(varTok, expr))

        # naked assignment (ID = Exp) support
        if tok.type == Consts.ID and self.parser.Lookahead(1).type == Consts.EQ:
            varTok = tok
            self.NextToken() 
            self.NextToken() 
            expr = ast.registry(Exp(self.parser).Rule())
            if ast.error: return ast
            return ast.success(NoVarAssign(varTok, expr))

        left = ast.registry(Term(self.parser).Rule())
        if ast.error: return ast
        while self.CurrentToken().type in (Consts.PLUS, Consts.MINUS):
            opTok = self.CurrentToken()
            self.NextToken()
            right = ast.registry(Term(self.parser).Rule())
            if ast.error: return ast
            left = NoOpBinaria(left, opTok, right)
        return ast.success(left)

##############################
# Term ::= Factor ((*|/) Factor)*
class Term(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        left = ast.registry(Factor(self.parser).Rule())
        if ast.error: return ast
        while self.CurrentToken().type in (Consts.MUL, Consts.DIV):
            opTok = self.CurrentToken()
            self.NextToken()
            right = ast.registry(Factor(self.parser).Rule())
            if ast.error: return ast
            left = NoOpBinaria(left, opTok, right)
        return ast.success(left)

##############################
# Factor ::= (PLUS | MINUS)* Factor | Pow
class Factor(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        # handle unary chain
        unary_ops = []
        while self.CurrentToken().type in (Consts.PLUS, Consts.MINUS):
            unary_ops.append(self.CurrentToken())
            self.NextToken()
        node = ast.registry(Pow(self.parser).Rule())
        if ast.error: return ast
        # apply in reverse (right to left)
        for opTok in reversed(unary_ops):
            node = NoUnary(opTok, node)
        return ast.success(node)

##############################
# Pow ::= Atom (POW Factor)?
class Pow(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        left = ast.registry(Atom(self.parser).Rule())
        if ast.error: return ast
        if self.CurrentToken().type == Consts.POW:
            opTok = self.CurrentToken()
            self.NextToken()
            right = ast.registry(Factor(self.parser).Rule())
            if ast.error: return ast
            left = NoOpBinaria(left, opTok, right)
        return ast.success(left)

##############################
# Atom ::= INT | FLOAT | STRING | ID | ListExp | TupleExp | LPAR Exp RPAR | FuncLiteral
class Atom(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        tok = self.CurrentToken()

        # Function literal: fn (params) -> Exp
        if tok.matches(Consts.KEY, Consts.FUNC):
            self.NextToken()  # 'fn'
            if self.CurrentToken().type != Consts.LPAR:
                return ast.fail(f"{Error.parserError}: Esperado '(' apos 'fn'")
            self.NextToken()  # '('
            params = []
            if self.CurrentToken().type != Consts.RPAR:
                if self.CurrentToken().type != Consts.ID:
                    return ast.fail(f"{Error.parserError}: Esperado identificador de parametro")
                params.append(self.CurrentToken().value)
                self.NextToken()
                while self.CurrentToken().type == Consts.COMMA:
                    self.NextToken()
                    if self.CurrentToken().type != Consts.ID:
                        return ast.fail(f"{Error.parserError}: Esperado identificador de parametro")
                    params.append(self.CurrentToken().value)
                    self.NextToken()
            if self.CurrentToken().type != Consts.RPAR:
                return ast.fail(f"{Error.parserError}: Esperado ')' ")
            self.NextToken()  # ')'
            if self.CurrentToken().type != Consts.ARROW:
                return ast.fail(f"{Error.parserError}: Esperado '->' apos parametros")
            self.NextToken()  # '->'
            body = ast.registry(Exp(self.parser).Rule())
            if ast.error: return ast
            node = NoFuncLiteral(params, body)
            while self.CurrentToken().type == Consts.LPAR:
                node = self._parse_call_suffix(node)
            return ast.success(node)

        if tok.type == Consts.LPAR:
            if self._is_tuple_start():
                return TupleExp(self.parser).Rule()
            self.NextToken()
            node = ast.registry(Exp(self.parser).Rule())
            if ast.error: return ast
            if self.CurrentToken().type != Consts.RPAR:
                return ast.fail(f"{Error.parserError}: Esperado ')' ")
            self.NextToken()
            while self.CurrentToken().type == Consts.LPAR:
                node = self._parse_call_suffix(node)
            return ast.success(node)

        # List
        if tok.type == Consts.LSQUARE:
            return ListExp(self.parser).Rule()

        # Numbers
        if tok.type == Consts.INT:
            self.NextToken()
            node = NoNumber(tok)
            while self.CurrentToken().type == Consts.LPAR:
                node = self._parse_call_suffix(node)
            return ast.success(node)
        if tok.type == Consts.FLOAT:
            self.NextToken()
            node = NoNumber(tok)
            while self.CurrentToken().type == Consts.LPAR:
                node = self._parse_call_suffix(node)
            return ast.success(node)
        # String
        if tok.type == Consts.STRING:
            self.NextToken()
            node = NoString(tok)
            while self.CurrentToken().type == Consts.LPAR:
                node = self._parse_call_suffix(node)
            return ast.success(node)
        # Variable / function call
        if tok.type == Consts.ID:
            self.NextToken()
            node = NoVarAccess(tok)
            while self.CurrentToken().type == Consts.LPAR:
                node = self._parse_call_suffix(node)
            return ast.success(node)

        return ast.fail(f"{Error.parserError}: Token inesperado em Atom: {tok}")

    def _parse_call_suffix(self, calleeNode):
        ast = self.GetParserManager()
        if self.CurrentToken().type != Consts.LPAR:
            return ast.fail(f"{Error.parserError}: Esperado '(' para chamada")
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
            return ast.fail(f"{Error.parserError}: Esperado ')' ")
        self.NextToken()  # ')'
        return NoCall(calleeNode, args)

    def _is_tuple_start(self):
        depth = 0
        i = 0
        while True:
            tok = self.parser.Lookahead(i)
            if tok.type == Consts.LPAR:
                depth += 1
            elif tok.type == Consts.RPAR:
                depth -= 1
                if depth == 0:
                    return False
            elif tok.type == Consts.COMMA and depth == 1:
                return True
            elif tok.type == Consts.EOF:
                return False
            i += 1

##############################
# ListExp ::= LSQUARE [ Exp (COMMA Exp)* ] RSQUARE
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
# TupleExp ::= LPAR Exp (COMMA Exp)+ RPAR
class TupleExp(Grammar):
    def Rule(self):
        ast = self.GetParserManager()
        if self.CurrentToken().type != Consts.LPAR:
            return ast.fail(f"{Error.parserError}: Esperado '(' para tupla")
        self.NextToken()
        elementNodes = []
        elementNodes.append(ast.registry(Exp(self.parser).Rule()))
        if ast.error: return ast

        if self.CurrentToken().type != Consts.COMMA:
            return ast.fail(f"{Error.parserError}: Esperando por ',' em tupla")

        while self.CurrentToken().type == Consts.COMMA:
            self.NextToken()
            elementNodes.append(ast.registry(Exp(self.parser).Rule()))
            if ast.error: return ast

        if self.CurrentToken().type != Consts.RPAR:
            return ast.fail(f"{Error.parserError}: Esperando por ')' em tupla")
        self.NextToken()

        return ast.success(NoTuple(elementNodes))
