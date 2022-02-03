from collections import deque

from sly import Parser

from .model import *
from .tokenizer import AHKLexer
from .tokenizer import tokenize


class AHKParser(Parser):
    debugfile = 'parser.out'
    tokens = AHKLexer.tokens

    @_('statements')
    def program(self, p):
        return p[0]

    # statements : { statement }      # zero or more statements { }
    @_('{ statement }')
    def statements(self, p):
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
        # 'for_statement',
        # 'try_statement',
        # 'variable_declaration',
        'expression_statement',
        'return_statement',
    )
    def statement(self, p):
        return p[0]

    @_('RETURN [ expression ]')
    def return_statement(self, p):
        return ReturnStatement(expression=p.expression)

    @_(
        # 'grouping'
        # 'deref'
        'function_call'
        # 'tenary_expression'
    )
    def expression_statement(self, p):
        return p[0]

    @_(
        'EXP',
        'PLUS',
        'MINUS',
        'TIMES',
        'DIVIDE',
        'LT',
        'LE',
        'GT',
        'GE',
        'EQ',
        'SEQ',
        'NE',
        'SNE',
        'LAND',
        'REMATCH',
        'LOR',
        'AND',
        'OR',
        'IN',
        'IS',
    )
    def bin_operator(self, p):
        return p[0]

    @_(
        'expression { WHITESPACE } bin_operator { WHITESPACE } expression',
        'expression { WHITESPACE } bin_operator { WHITESPACE } expression',
        'expression { WHITESPACE } bin_operator { WHITESPACE } expression',
        'expression { WHITESPACE } bin_operator { WHITESPACE } expression',
        'expression { WHITESPACE } bin_operator { WHITESPACE } expression',
        'expression { WHITESPACE } bin_operator { WHITESPACE } expression',
        'expression { WHITESPACE } bin_operator { WHITESPACE } expression',
        'expression { WHITESPACE } bin_operator { WHITESPACE } expression',
        'expression { WHITESPACE } bin_operator { WHITESPACE } expression',
        'expression { WHITESPACE } bin_operator { WHITESPACE } expression',
        'expression { WHITESPACE } bin_operator { WHITESPACE } expression',
        'expression { WHITESPACE } bin_operator { WHITESPACE } expression',
        'expression { WHITESPACE } bin_operator { WHITESPACE } expression',
        'expression { WHITESPACE } bin_operator { WHITESPACE } expression',
        'expression { WHITESPACE } bin_operator { WHITESPACE } expression',
        'expression { WHITESPACE } bin_operator { WHITESPACE } expression',
        'expression { WHITESPACE } bin_operator { WHITESPACE } expression',
        'expression { WHITESPACE } bin_operator { WHITESPACE } expression',
        'expression { WHITESPACE } bin_operator { WHITESPACE } expression',
        'expression { WHITESPACE } bin_operator { WHITESPACE } expression',
    )
    def bin_op(self, p):
        op = p[2]
        left = p.expression0
        right = p.expression1
        return BinOp(op=op, left=left, right=right)

    @_('NAME')
    def location(self, p):
        return Identifier(name=p.NAME)

    @_('TRUE')
    def expression(self):
        return Bool(True)

    @_('FALSE')
    def expression(self):
        return Bool(False)

    @_(
        'expression_statement',
        'bin_op',
        'location',
    )
    def expression(self, p):
        return p[0]

    @_('NAME LPAREN { WHITESPACE } [ arguments ] { WHITESPACE } RPAREN')
    def function_call(self, p):
        function_name = p.NAME
        return FunctionCall(name=function_name, arguments=p.arguments)

    @_('INTEGER')
    def expression(self, p):
        return Integer(value=int(p.INTEGER))

    @_('NEWLINE { WHITESPACE } NAME { WHITESPACE } [ arguments ] terminator')
    def function_call(self, p):
        return FunctionCall(name=p.NAME, arguments=p.arguments)

    @_('{ WHITESPACE } expression')
    def additional_arguments(self, p):
        return p.expression

    @_('expression { WHITESPACE } { COMMA additional_arguments }')
    def arguments(self, p):
        args = [p.expression]
        for a in p.additional_arguments:
            args.append(a)
        return args

    @_('location { WHITESPACE } ASSIGN { WHITESPACE } expression terminator')
    def assignment_statement(self, p):
        return Assignment(location=p.location, value=p.expression)

    @_('NEWLINE')
    def terminator(self, p):
        return p[0]


def parse_tokens(raw_tokens):
    parser = AHKParser()
    return parser.parse(raw_tokens)


def parse_source(text):
    tokens = tokenize(text)
    model = parse_tokens(tokens)
    return model
