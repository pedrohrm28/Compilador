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
    COLON     = ':'       
    DOT       = '.'       
    LPAR      = '('
    RPAR      = ')'
    LSQUARE   = '['
    RSQUARE   = ']'
    LBRACE    = '{'       
    RBRACE    = '}'       

    EOF       = '$EOF'

    # Palavras reservadas
    LET       = 'let'
    IF        = 'if'
    WHILE     = 'while'
    FOR       = 'for'
    FUNC      = 'fn'
    RETURN    = 'return'
    TO     = 'to'       # NEW
    DO     = 'do'       # NEW
    STEP   = 'step'

    KEYS = [
        LET,
        IF,
        WHILE,
        FOR,
        FUNC,
        RETURN,
        TO,
        DO,
        STEP
    ]
