from Consts import Consts
from Token import Token
from Error import Error

class Lexer:
    def __init__(self, source_code):
        self.code = source_code or ''
        self.current = None
        self.indice, self.coluna, self.linha = -1, -1, 1
        self.__advance()

    def __advance(self):
        if self.current == '\n':
            self.linha += 1
            self.coluna = 0
        else:
            self.coluna += 1
        self.indice += 1
        self.current = self.code[self.indice] if self.indice < len(self.code) else None

    def lex(self):
        tokens = []
        while self.current is not None:
            c = self.current

            # whitespace
            if c in ' \t\r':
                self.__advance(); continue
            if c == '\n':
                self.__advance(); continue

            # comments
            if c == '/' and self.__peek() == '/':
                self.__advance(); self.__advance()
                while self.current not in (None, '\n'):
                    self.__advance()
                continue
            if c == '#':
                while self.current not in (None, '\n'):
                    self.__advance()
                continue

            # two-char ops
            if c == '-' and self.__peek() == '>':
                self.__advance(); self.__advance()
                tokens.append(Token(Consts.ARROW)); continue

            # strings
            if c == '"':
                tokens.append(self.__makeString()); continue

            # numbers
            if c.isdigit():
                tokens.append(self.__makeNumber()); continue

            # identifiers / keywords
            if c.isalpha() or c == Consts.UNDER:
                tokens.append(self.__makeId()); continue

            # single-char symbols
            if c == '+': tokens.append(Token(Consts.PLUS)); self.__advance(); continue
            if c == '-': tokens.append(Token(Consts.MINUS)); self.__advance(); continue
            if c == '*': tokens.append(Token(Consts.MUL)); self.__advance(); continue
            if c == '/': tokens.append(Token(Consts.DIV)); self.__advance(); continue
            if c == '^': tokens.append(Token(Consts.POW)); self.__advance(); continue
            if c == '=': tokens.append(Token(Consts.EQ)); self.__advance(); continue
            if c == '(': tokens.append(Token(Consts.LPAR)); self.__advance(); continue
            if c == ')': tokens.append(Token(Consts.RPAR)); self.__advance(); continue
            if c == '[': tokens.append(Token(Consts.LSQUARE)); self.__advance(); continue
            if c == ']': tokens.append(Token(Consts.RSQUARE)); self.__advance(); continue
            if c == '{': tokens.append(Token(Consts.LBRACE)); self.__advance(); continue  # NEW
            if c == '}': tokens.append(Token(Consts.RBRACE)); self.__advance(); continue  # NEW
            if c == ',': tokens.append(Token(Consts.COMMA)); self.__advance(); continue
            if c == ':': tokens.append(Token(Consts.COLON)); self.__advance(); continue   # NEW
            if c == '.': tokens.append(Token(Consts.DOT)); self.__advance(); continue     # NEW

            raise Exception(Error(f"{Error.lexerError}: caractere inesperado '{c}' na linha {self.linha}, coluna {self.coluna}"))

        tokens.append(Token(Consts.EOF))
        return tokens

    # compat com REPL antigo
    def makeTokens(self):
        try:
            toks = self.lex()
            return toks, None
        except Exception as e:
            return [], e

    def __peek(self, k=1):
        idx = self.indice + k
        return self.code[idx] if idx < len(self.code) else None

    def __makeNumber(self):
        num_str = ''
        dot_count = 0
        while self.current is not None and (self.current.isdigit() or self.current == '.'):
            if self.current == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current
            self.__advance()
        if num_str.startswith('.'): num_str = '0' + num_str
        if num_str.endswith('.'): num_str += '0'
        if dot_count == 0:
            return Token(Consts.INT, int(num_str))
        else:
            return Token(Consts.FLOAT, float(num_str))

    def __makeString(self):
        self.__advance()
        chars, escape = [], False
        while self.current is not None:
            c = self.current
            if escape:
                if c == 'n': chars.append('\n')
                elif c == 't': chars.append('\t')
                elif c == '"': chars.append('"')
                elif c == '\\': chars.append('\\')
                else: chars.append(c)
                escape = False
                self.__advance(); continue
            if c == '\\':
                escape = True
                self.__advance(); continue
            if c == '"':
                self.__advance()
                return Token(Consts.STRING, ''.join(chars))
            chars.append(c)
            self.__advance()
        raise Exception(Error(f"{Error.lexerError}: string não finalizada"))

    def __makeId(self):
        lexema = ''
        while self.current is not None and (self.current.isalnum() or self.current == Consts.UNDER):
            lexema += self.current
            self.__advance()
        tokType = Consts.KEY if lexema in Consts.KEYS else Consts.ID
        return Token(tokType, lexema)
