import logging
import sys

import regex as re
from sly import Lexer
from sly.lex import Token

from .utils import AHKTokenizeError

logger = logging.getLogger(__name__)
# logger.addHandler(logging.StreamHandler(stream=sys.stderr))
# logger.setLevel(level=logging.DEBUG)
class AHKToken(Token):
    '''
    Representation of a single token.
    '''

    def __init__(self, tok, doc):
        self.type = tok.type
        self.value = tok.value
        self.lineno = tok.lineno
        self.index = tok.index
        self.doc = doc

    __slots__ = ('type', 'value', 'lineno', 'index', 'doc')

    def __repr__(self):
        return f'AHKToken(type={self.type!r}, value={self.value!r}, lineno={self.lineno}, index={self.index})'


class AHKLexer(Lexer):
    def __init__(self, *args, **kwargs):
        self._include_comments = kwargs.pop('include_whitespace', True)
        super().__init__(*args, **kwargs)

    regex_module = re
    reflags = re.MULTILINE
    tokens = {
        ARROW,
        AMP,
        HASH,
        LBRACE,
        RBRACE,
        LBRACKET,
        RBRACKET,
        DOUBLE_QUOTE_STRING,
        SINGLE_QUOTE_STRING,
        UNTERMINATED_DOUBLE_QUOTE_STRING,
        UNTERMINATED_SINGLE_QUOTE_STRING,
        NAME,
        COMMA,
        BLOCK_COMMENT,
        LINE_COMMENT,
        WHITESPACE,
        TRUE,
        FALSE,
        NULL,
        COLON,
        DCOLON,
        DOT,
        # Operators
        LE,
        LT,
        GE,
        GT,
        EQ,
        SEQ,
        NE,
        SNE,
        ASSIGN,
        LPAREN,
        RPAREN,
        REMATCH,
        QUESTION,
        PERCENT,
        TILDE,
        PIPE,
        # CARET,
        BSHIFTL,
        BSHIFTR,
        LSHIFTR,
        BOR,
        LOR,
        LAND,
        LNOT,
        PLUS,
        INCR,
        MINUS,
        DECR,
        FLOAT,
        INTEGER,
        TIMES,
        EXP,
        DIVIDE,
        INT_DIVIDE,
        # Reserved words
        AND,
        AS,
        BREAK,
        CATCH,
        CONTAINS,
        CONTINUE,
        ELSE,
        FINALLY,
        FOR,
        GLOBAL,
        GOTO,
        IF,
        IN,
        IS,
        ISSET,
        LOCAL,
        LOOP,
        LOOP_COUNT,
        LOOP_FILES,
        LOOP_PARSE,
        LOOP_READ,
        LOOP_REG,
        NOT,
        OR,
        RETURN,
        STATIC,
        SUPER,
        THROW,
        TRY,
        UNSET,
        UNTIL,
        WHILE,
        CLASS,
    }

    # print(tokens)
    # ignore = ' \t'  # Ignore these (between tokens)

    # @_(r'\n+')
    # def ignore_newline(self, tok):
    #     self.lineno += tok.value.count('\n')

    @_(r'/\*((.|\n))*?\*/')
    def BLOCK_COMMENT(self, tok):
        self.lineno += tok.value.count('\n')
        if self._include_comments:
            return tok

    @_(r'[\u0009\u000B\u000C\u000D\u0020\u00A0\u2028\u2029\ufeff];[^\n]*')
    def INLINE_COMMENT(self, tok):
        if self._include_comments:
            return tok

    @_(r'^;[^\n]*')
    def LINE_COMMENT(self, tok):
        if self._include_comments:
            return tok

    # _escape_sequences = [
    #     r'``',
    #     r"`'",
    #     r'`"',
    #     r'`[nrbtsvaf]',
    #     r'`:',
    #     r'`;',
    #     # r'\\\d{1,3}',
    #     # r'\\x[a-fA-F0-9]{1,2}',
    # ]
    DOUBLE_QUOTE_STRING = r'"(?:[^"`]|`.)*"'
    SINGLE_QUOTE_STRING = r"'(?:[^'`]|`.)*'"

    # Specify tokens as regex rules
    HASH = r'#'
    BSHIFTL = r'<<'
    LSHIFTR = r'>>>'
    BSHIFTR = r'>>'
    PERCENT = r'%'
    LBRACKET = r'\['
    RBRACKET = r'\]'
    # CARET = r'\^'
    BOR = r'\^'
    QUESTION = r'\?'
    COMMA = r','
    INCR = r'\+\+'
    PLUS = r'\+'
    MINUS = r'-'
    DECR = r'--'
    EXP = r'\*\*'
    TIMES = r'\*'
    INT_DIVIDE = r'//'
    DIVIDE = r'/'
    FLOAT = r'(\d+\.\d*)|(\d*\.\d+)'  # 23.45
    INTEGER = r'\d+'
    # CHAR = r'\'(.|' + '|'.join(_escape_sequences) + r')\''
    DOT = r'\.'
    # LOOKUP = r'\.[a-zA-Z_]([a-zA-Z_\d])*'

    # Reserved Keywords
    CLASS = r'(?i)class'
    IF = r'(?i)if'
    ELSE = r'(?i)else'
    WHILE = r'(?i)while'
    FOR = r'(?i)for'
    TRY = r'(?i)try'
    CATCH = r'(?i)catch'
    FINALLY = r'(?i)finally'
    RETURN = r'(?i)return'
    GOTO = r'(?i)goto'
    CONTINUE = r'(?i)continue'
    UNTIL = r'(?i)until'
    LOOP_COUNT = r'(?i)loop count'
    LOOP_REG = r'(?i)loop reg'
    LOOP_FILES = r'(?i)loop files'
    LOOP_PARSE = r'(?i)loop parse'
    LOOP_READ = r'(?i)loop read'
    LOOP = r'(?i)loop'
    BREAK = r'(?i)break'
    AS = r'(?i)as'
    AND = r'(?i)and'
    CONTAINS = r'(?i)contains'
    IN = r'(?i)in'
    IS = r'(?i)is'
    ISSET = r'(?i)isset'
    NOT = r'(?i)not'
    OR = r'(?i)or'
    SUPER = r'(?i)super'
    UNSET = r'(?i)unset'
    GLOBAL = r'(?i)global'
    LOCAL = r'(?i)local'
    THROW = r'(?i)throw'
    STATIC = r'(?i)static'
    TRUE = r'(?i)true'
    FALSE = r'(?i)false'

    NAME = r'[a-zA-Z_]([a-zA-Z_\d])*'

    @_('\u000A')
    def NEWLINE(self, tok: AHKToken):
        self.lineno += 1
        return tok

    @_('[\u0009\u000B\u000C\u000D\u0020\u00A0\u2028\u2029\ufeff]+')
    def WHITESPACE(self, tok: AHKToken):
        # We need to capture whitespace tokens because AHK has some sensitivity to whitespace
        # For example ``func()`` is valid, but ``func ()`` is not.
        # see: https://lexikos.github.io/v2/docs/Language.htm#general-conventions
        self.lineno += tok.value.count('\n')
        return tok

    # Put longer patterns first

    ARROW = r'=>'
    LE = r'<='
    LT = r'<'  # Order matters a lot. Definition order is the order matches are tried.
    GE = r'>='
    GT = r'>'
    REMATCH = r'~='
    TILDE = r'~'
    SEQ = r'=='
    EQ = r'='
    SNE = r'!=='
    NE = r'!='
    ASSIGN = r':='
    # SEMI = r';'
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACE = r'{'
    RBRACE = r'}'
    LOR = r'\|\|'
    PIPE = r'\|'
    LAND = r'&&'
    AMP = r'&'
    LNOT = r'!'
    DCOLON = r'::'
    COLON = r':'

    def tokenize(self, text, *args, **kwargs):
        for tok in super().tokenize(text, *args, **kwargs):
            tok = AHKToken(tok, text)
            yield tok

    def error(self, t: AHKToken):
        raise AHKTokenizeError(
            f'Illegal character {t.value[0]!r} at index {self.index} (line {self.lineno})', None
        )


def tokenize(text):
    lexer = AHKLexer()
    tokens = lexer.tokenize(text)
    return tokens


# Main program to test on input files
def main(filename):
    with open(filename) as file:
        text = file.read()

    for tok in tokenize(text):
        print(tok)


if __name__ == '__main__':
    import sys

    main(sys.argv[1])
