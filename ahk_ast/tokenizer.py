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
        NEWLINE,
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
    CLASS = r'(?i)class(?![a-zA-Z_\d]+)'
    IF = r'(?i)if(?![a-zA-Z_\d]+)'
    ELSE = r'(?i)else(?![a-zA-Z_\d]+)'
    WHILE = r'(?i)while(?![a-zA-Z_\d]+)'
    FOR = r'(?i)for(?![a-zA-Z_\d]+)'
    TRY = r'(?i)try(?![a-zA-Z_\d]+)'
    CATCH = r'(?i)catch(?![a-zA-Z_\d]+)'
    FINALLY = r'(?i)finally(?![a-zA-Z_\d]+)'
    RETURN = r'(?i)return(?![a-zA-Z_\d]+)'
    GOTO = r'(?i)goto(?![a-zA-Z_\d]+)'
    CONTINUE = r'(?i)continue(?![a-zA-Z_\d]+)'
    UNTIL = r'(?i)until(?![a-zA-Z_\d]+)'
    LOOP_COUNT = r'(?i)loop count(?![a-zA-Z_\d]+)'
    LOOP_REG = r'(?i)loop reg(?![a-zA-Z_\d]+)'
    LOOP_FILES = r'(?i)loop files(?![a-zA-Z_\d]+)'
    LOOP_PARSE = r'(?i)loop parse(?![a-zA-Z_\d]+)'
    LOOP_READ = r'(?i)loop read(?![a-zA-Z_\d]+)'
    LOOP = r'(?i)loop(?![a-zA-Z_\d]+)'
    BREAK = r'(?i)break(?![a-zA-Z_\d]+)'
    AS = r'(?i)as(?![a-zA-Z_\d]+)'
    AND = r'(?i)and(?![a-zA-Z_\d]+)'
    CONTAINS = r'(?i)contains(?![a-zA-Z_\d]+)'
    IN = r'(?i)in(?![a-zA-Z_\d]+)'
    IS = r'(?i)is(?![a-zA-Z_\d]+)'
    ISSET = r'(?i)isset(?![a-zA-Z_\d]+)'
    NOT = r'(?i)not(?![a-zA-Z_\d]+)'
    OR = r'(?i)or(?![a-zA-Z_\d]+)'
    SUPER = r'(?i)super(?![a-zA-Z_\d]+)'
    UNSET = r'(?i)unset(?![a-zA-Z_\d]+)'
    GLOBAL = r'(?i)global(?![a-zA-Z_\d]+)'
    LOCAL = r'(?i)local(?![a-zA-Z_\d]+)'
    THROW = r'(?i)throw(?![a-zA-Z_\d]+)'
    STATIC = r'(?i)static(?![a-zA-Z_\d]+)'
    TRUE = r'(?i)true(?![a-zA-Z_\d]+)'
    FALSE = r'(?i)false(?![a-zA-Z_\d]+)'

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
