import string

class Consts:
    DIGITOS = '0123456789'
    LETRAS = string.ascii_letters
    LETRAS_DIGITOS = DIGITOS + LETRAS
    UNDER = '_'

    # Token types
    INT       = 'INT'
    FLOAT     = 'FLOAT'
    STRING    = 'STRING'
    ID        = 'ID'
    KEY       = 'KEY'

    PLUS      = '+'
    MINUS     = '-'
    MUL       = '*'
    DIV       = '/'
    POW       = '^'

    EQ        = '='
    ARROW     = '->'
    COMMA     = ','
    LPAR      = '('
    RPAR      = ')'
    LSQUARE   = '['
    RSQUARE   = ']'

    EOF       = '$EOF'

    # Palavras reservadas
    LET       = 'let'
    IF        = 'if'
    WHILE     = 'while'
    FOR       = 'for'
    FUNC      = 'fn'
    RETURN    = 'return'

    KEYS = [
        LET,
        IF,
        WHILE,
        FOR,
        FUNC,
        RETURN
    ]
