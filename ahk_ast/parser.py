from typing import Any
from typing import Sequence
from typing import Union

from sly import Parser  # type: ignore[import]
from sly.lex import Token  # type: ignore[import]
from sly.yacc import YaccProduction  # type: ignore[import]

from .errors import AHKAstBaseException
from .errors import InvalidHotkeyException
from .model import *
from .tokenizer import AHKLexer
from .tokenizer import AHKToken
from .tokenizer import tokenize


class AHKParser(Parser):
    debugfile = 'parser.out'
    tokens = AHKLexer.tokens
    precedence = [
        ('left', LOR, OR),  # a || b
        ('left', LAND, AND),  # a && b
        (
            'left',
            LT,
            LE,
            GT,
            GE,
            EQ,
            NE,
            SEQ,
            SNE,
            REMATCH,
            IN,
            IS,
        ),  #  2 + 3 < 4 + 5   -> (2 + 3) <  (4 + 5)
        ('left', PLUS, MINUS),  # Lower precedence      2 + 3 + 4 --> (2+3) + 4
        (
            'left',
            TIMES,
            DIVIDE,
        ),
        ('left', EXP),
        ('left', TERNARY),
        ('right', DEREF),
        ('right', DOUBLE_DEREF)
        # Higher precedence     2 + 3 * 4 --> 2 + (3 * 4)  (preference for the TIMES)
        # Unary -x.   -> Super high precedence    2 * -x.
        # ("right", UNARY),  # 'UNARY' is a fake token (does not exist in tokenizer)
    ]

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.errors: list[AHKAstBaseException]
        self.errors = []
        self.last_token: Union[AHKToken, None]
        self.last_token = None
        self.seen_tokens: list[AHKToken]
        self.seen_tokens = []
        self.expecting: list[AHKToken]
        self.expecting = []

    @_('statements')
    def program(self, p: YaccProduction) -> Any:
        return p[0]

    # statements : { statement }      # zero or more statements { }
    @_('{ statement }')
    def statements(self, p: YaccProduction) -> Any:
        # p.statement   --- it's already a list of statement (by SLY)
        return Program(*p.statement)

    @_(
        'assignment_statement',
        # 'augmented_assignment_statement',
        # 'if_statement',
        # 'loop_statement',
        # 'while_statement',
        # 'class_definition',
        # 'function_definition',
        # 'hotkey_definition',
        # 'for_statement',
        # 'try_statement',
        # 'variable_declaration',
        # 'expression_statement',
        'return_statement',
        'function_call_statement',
    )
    def statement(self, p: YaccProduction) -> Any:
        return p[0]

    @_('RETURN [ WHITESPACE expression ]')
    def return_statement(self, p: YaccProduction) -> Any:
        return ReturnStatement(expression=p.expression)

    @_('PERCENT NAME %prec DEREF', 'PERCENT NAME PERCENT %prec DOUBLE_DEREF')
    def location(self, p: YaccProduction) -> Any:
        return Identifier(name=p.name)

    @_(
        # 'grouping'
        'ternary_expression',
        'function_call',
        'location',
    )
    def expression_statement(self, p: YaccProduction) -> Any:
        return p[0]

    @_(
        'expression EXP [ WHITESPACE ] expression',
        'expression PLUS [ WHITESPACE ] expression',
        'expression MINUS [ WHITESPACE ] expression',
        'expression TIMES [ WHITESPACE ] expression',
        'expression DIVIDE [ WHITESPACE ] expression',
        'expression LT [ WHITESPACE ] expression',
        'expression LE [ WHITESPACE ] expression',
        'expression GT [ WHITESPACE ] expression',
        'expression GE [ WHITESPACE ] expression',
        'expression EQ [ WHITESPACE ] expression',
        'expression SEQ [ WHITESPACE ] expression',
        'expression NE [ WHITESPACE ] expression',
        'expression SNE [ WHITESPACE ] expression',
        'expression LAND [ WHITESPACE ] expression',
        'expression REMATCH [ WHITESPACE ] expression',
        'expression LOR [ WHITESPACE ] expression',
        'expression AND [ WHITESPACE ] expression',
        'expression OR [ WHITESPACE ] expression',
        'expression IN [ WHITESPACE ] expression',
        'expression IS [ WHITESPACE ] expression',
    )
    def bin_op(self, p: YaccProduction) -> Any:
        op = p[1]
        left = p.expression0
        right = p.expression1
        return BinOp(op=op, left=left, right=right)

    @_(
        'expression QUESTION [ WHITESPACE ] expression COLON [ WHITESPACE ] expression %prec TERNARY'
    )
    def ternary_expression(self, p: YaccProduction) -> Any:
        condition = p.expression0
        consequent = p.expression1
        alternative = p.expression2
        return TernaryExpression(
            condition=condition, consequent=consequent, alternative=alternative
        )

    @_('NAME')
    def location(self, p: YaccProduction) -> Any:
        return Identifier(name=p.NAME)

    @_('TRUE')
    def expression(self) -> Any:
        return Bool(True)

    @_('FALSE')
    def expression(self) -> Any:
        return Bool(False)

    @_(
        'expression_statement',
        'bin_op',
    )
    def expression(self, p: YaccProduction) -> Any:
        return p[0]

    @_('NAME LPAREN [ WHITESPACE ] RPAREN')
    def function_call(self, p: YaccProduction) -> Any:
        return FunctionCall(name=p.NAME, arguments=None)

    @_('NAME LPAREN [ WHITESPACE ] arguments RPAREN')
    def function_call(self, p: YaccProduction) -> Any:
        function_name = p.NAME
        return FunctionCall(name=function_name, arguments=p.arguments)

    @_('INTEGER')
    def expression(self, p: YaccProduction) -> Any:
        return Integer(value=int(p.INTEGER))

    @_('NEWLINE [ WHITESPACE ] NAME [ WHITESPACE ] [ arguments ] terminator')
    def function_call_statement(self, p: YaccProduction) -> FunctionCall:
        return FunctionCall(name=p.NAME, arguments=p.arguments)

    @_('COMMA [ WHITESPACE ] first_argument')
    def additional_arguments(self, p: YaccProduction) -> Any:
        return p.first_argument

    @_('expression')
    def first_argument(self, p: YaccProduction) -> Any:
        return p[0]

    @_('first_argument { additional_arguments }')
    def arguments(self, p: YaccProduction) -> Any:
        args = [p.first_argument]
        for a in p.additional_arguments:
            args.append(a)
        return args

    @_('location [ WHITESPACE ] ASSIGN [ WHITESPACE ] expression terminator')
    def assignment_statement(self, p: YaccProduction) -> Any:
        return Assignment(location=p.location, value=p.expression)

    @_('NEWLINE')
    def terminator(self, p: YaccProduction) -> Any:
        return p[0]

    @_('expression WHITESPACE')
    def expression(self, p: YaccProduction) -> Any:
        return p[0]


def parse_tokens(raw_tokens: Iterable['Token']) -> Node:
    parser = AHKParser()
    return parser.parse(raw_tokens)  # type: ignore[no-any-return]


def parse(text: str) -> Node:
    tokens = tokenize(text)
    model = parse_tokens(tokens)
    return model
