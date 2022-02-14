import sys
from typing import Any
from typing import Generator
from typing import NoReturn
from typing import Sequence
from typing import Union

from sly import Parser  # type: ignore[import]
from sly.lex import Token  # type: ignore[import]
from sly.yacc import YaccProduction  # type: ignore[import]

from .errors import AHKAstBaseException
from .errors import AHKDecodeError
from .errors import AHKParsingException
from .errors import InvalidHotkeyException
from .model import *
from .tokenizer import AHKLexer
from .tokenizer import AHKToken
from .tokenizer import tokenize


class AHKParser(Parser):
    debugfile = 'parser.out'
    tokens = AHKLexer.tokens
    start = 'program'

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.errors: list[AHKAstBaseException]
        self.errors = []
        self.last_token: Union[AHKToken, None]
        self.last_token = None
        self.seen_tokens: list[AHKToken]
        self.seen_tokens = []
        self.expecting: list[list[str]]
        self.expecting = []

    @_('WHITESPACE', 'NEWLINE')
    def wsc(self, p: YaccProduction) -> Any:
        return p[0]

    @_('{ wsc } statements { wsc }')
    def program(self, p: YaccProduction) -> Any:
        return Program(*p.statements)

    @_('NEWLINE [ WHITESPACE ] [ statements ]')
    def additional_statement(self, p: YaccProduction) -> Any:
        return p.statements

    @_('statement { additional_statement }')
    def statements(self, p: YaccProduction) -> Any:
        ret = [p.statement]
        for stmts in p.additional_statement:
            if stmts:
                ret.extend(stmts)
        return ret

    @_('assignment_statement', 'function_call_statement', 'function_call')
    def statement(self, p: YaccProduction) -> Any:
        return p[0]

    @_('NAME')
    def location(self, p: YaccProduction) -> Any:
        return Identifier(name=p[0])

    @_('')
    def seen_ASSIGN(self, p: YaccProduction) -> Any:
        self.expecting.append(['expression'])

    @_('location [ WHITESPACE ] ASSIGN seen_ASSIGN [ WHITESPACE ] expression')
    def assignment_statement(self, p: YaccProduction) -> Assignment:
        return Assignment(location=p.location, value=p.expression)

    @_('literal', 'location')
    def expression(self, p: YaccProduction) -> Any:
        self.expecting.pop()
        return p[0]

    @_('INTEGER')
    def literal(self, p: YaccProduction) -> Integer:
        return Integer(value=int(p[0]))

    @_('DOUBLE_QUOTED_STRING')
    def string(self, p: YaccProduction) -> DoubleQuotedString:
        # TODO: unescape value
        return DoubleQuotedString(value=p[0][1:-1])

    @_('SINGLE_QUOTED_STRING')
    def string(self, p: YaccProduction) -> SingleQuotedString:
        # TODO: unescape value
        return SingleQuotedString(value=p[0][1:-1])

    @_('string')
    def literal(self, p: YaccProduction) -> Any:
        return p[0]

    @_('')
    def seen_additional_arguments(self, p: YaccProduction) -> Any:
        self.expecting.append(['expression'])

    @_('COMMA [ WHITESPACE ] [ seen_additional_arguments first_argument ]')
    def additional_arguments(self, p: YaccProduction) -> Any:
        return p.first_argument

    @_('expression [ WHITESPACE ]')
    def first_argument(self, p: YaccProduction) -> Any:
        return p[0]

    @_('first_argument { additional_arguments }')
    def function_call_arguments(self, p: YaccProduction) -> Any:
        args = [p.first_argument]
        for a in p.additional_arguments:
            args.append(a)
        return args

    @_('')
    def seen_function_call_arguments_start(self, p: YaccProduction) -> Any:
        self.expecting.append(['expression'])

    @_('location [ WHITESPACE ] [ seen_function_call_arguments_start function_call_arguments ]')
    def function_call_statement(self, p: YaccProduction) -> FunctionCallStatement:
        return FunctionCallStatement(
            func_location=p.location,
            arguments=[arg for arg in p.function_call_arguments if arg]
            if p.function_call_arguments
            else None,
        )

    @_('')
    def function_call_seen(self, p: YaccProduction) -> Any:
        self.expecting.append(['RPAREN'])

    @_('')
    def seen_RPAREN(self, p: YaccProduction) -> Any:
        self.expecting.pop()

    @_(
        'location LPAREN function_call_seen [ WHITESPACE ] [ seen_function_call_arguments_start function_call_arguments ] seen_RPAREN RPAREN'
    )
    def function_call(self, p: YaccProduction) -> FunctionCall:
        return FunctionCall(
            func_location=p.location,
            arguments=[arg for arg in p.function_call_arguments if arg]
            if p.function_call_arguments
            else None,
        )

    def error(self, token: Union[AHKToken, None]) -> NoReturn:
        if token:
            if self.expecting:
                expected = self.expecting[-1]

                message = f"Syntax Error. Was expecting {' or '.join(expected)}"
            else:
                message = 'Syntax Error'
            raise AHKParsingException(message, token)

        elif self.last_token:
            doc = self.last_token.doc
            pos = len(doc)
            lineno = doc.count('\n', 0, pos) + 1
            colno = pos - doc.rfind('\n', 0, pos)
            message = f'Unexpected EOF at: ' f'line {lineno} column {colno} (char {pos})'
            if self.expecting:
                expected = self.expecting[-1]
                message += f'. Was expecting {" or ".join(expected)}'
            raise AHKParsingException(message, None)
        else:
            #  Empty file
            raise AHKParsingException(
                'Expecting at least one statement. Received unexpected EOF', None
            )

    def _token_gen(self, tokens: Iterable[AHKToken]) -> Generator[AHKToken, None, None]:
        for tok in tokens:
            # if self.last_token is None and tok.type != "NEWLINE":
            #     class t(Token):
            #         type = "NEWLINE"
            #         index = 0
            #         lineno = 0
            #         value = '\n'
            #     yield AHKToken(tok=t(), doc=tok.doc)
            self.last_token = tok
            self.seen_tokens.append(tok)
            yield tok

    def parse(self, tokens: Iterable[AHKToken]) -> Program:
        tokens = self._token_gen(tokens)
        model: Program
        model = super().parse(tokens)
        return model


def parse_tokens(raw_tokens: Iterable['Token']) -> Node:
    parser = AHKParser()
    return parser.parse(raw_tokens)


def parse(text: str) -> Node:
    tokens = tokenize(text)
    model = parse_tokens(tokens)
    return model


if __name__ == '__main__':
    fp = sys.argv[1]
    with open(fp) as f:
        text = f.read()
    print(parse(text))
