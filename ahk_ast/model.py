from collections.abc import Iterable
from textwrap import dedent
from types import SimpleNamespace as _SimpleNamespace


class Node(_SimpleNamespace):
    def __eq__(self, other: 'Node'):
        if not isinstance(other, Node):
            return False
        for key, value in self.__dict__.items():
            if key.startswith('_'):
                continue
            if key not in other.__dict__:
                print(key)
                return False
            if other.__dict__.get(key) != value:
                print(key)
                return False
        return True

    def __repr__(self):
        rep = (
            f'{self.__class__.__name__}('
            + ', '.join(
                '{key}={value}'.format(key=key, value=repr(value))
                for key, value in self.__dict__.items()
            )
            + ')'
        )
        try:
            return black_format_code(rep)
        except ImportError as e:
            # Just in case you don't have `black` installed :-)
            return rep
        except Exception as e:
            print('WARN: Unexpected error formatting code ', e)
            return rep


class Statement(Node):
    ...


class Definition(Statement):
    ...


class Expression(Node):
    ...


class Location(Expression):
    ...


class ExpressionStatement(Expression, Statement):
    """
    Expressions on their own CAN be statements
    """

    ...


class FieldLookup(Location):
    """
    p.x
    p.y
    """

    def __init__(self, location, fieldname, nested=False):
        assert isinstance(
            location, Location
        ), f'Expected Location. got {type(location)} {repr(location)}'
        assert isinstance(fieldname, str), f'Expected str. got {type(fieldname)}'
        super().__init__(location=location, fieldname=fieldname, nested=nested)


class Integer(Expression):
    """
    Example: 42
    """

    def __init__(self, value):
        assert isinstance(value, int)
        super().__init__(value=value)


class Float(Expression):
    """
    Example: 42.0
    """

    def __init__(self, value):
        assert isinstance(value, float)
        super().__init__(value=value)


class Bool(Expression):
    def __init__(self, value):
        assert isinstance(value, bool)
        super().__init__(value=value)


class UnaryOp(Expression):
    def __init__(self, op, operand):
        assert isinstance(op, str)
        assert op in ('+', '-', '!'), f'Invalid Unary operand: {op}'
        assert isinstance(operand, Expression)
        super().__init__(op=op, operand=operand)


class Identifier(Location):
    def __init__(self, name):
        assert isinstance(name, str)
        super().__init__(name=name)


class BinOp(Expression):
    """
    Example: left + right
    """

    def __init__(self, op, left, right):
        assert isinstance(op, str)
        assert op in (
            '+',
            '-',
            '*',
            '/',
            '<',
            '<=',
            '>=',
            '>',
            '=',
            '==',
            '!==',
            '!=',
            '&&',
            '||',
        ), f'Operation {op} is invalid'
        assert isinstance(left, Expression)
        assert isinstance(right, Expression)
        super().__init__(op=op, left=left, right=right)

    @classmethod
    def add(cls, left, right):
        return cls(op='+', left=left, right=right)

    @classmethod
    def subtract(cls, left, right):
        return cls(op='-', left=left, right=right)

    @classmethod
    def mult(cls, left, right):
        return cls(op='*', left=left, right=right)

    @classmethod
    def div(cls, left, right):
        return cls(op='/', left=left, right=right)


class Compare(BinOp):
    """
    ==, !=, <, >, <=, >=
    Comparisons operations always end up being Bools
    """

    @classmethod
    def lt(cls, left, right):
        return cls(left=left, right=right, op='<')

    @classmethod
    def lte(cls, left, right):
        return cls(left=left, right=right, op='<=')

    @classmethod
    def gt(cls, left, right):
        return cls(left=left, right=right, op='>')

    @classmethod
    def gte(cls, left, right):
        return cls(left=left, right=right, op='>=')

    @classmethod
    def eq(cls, left, right):
        return cls(left=left, right=right, op='==')

    @classmethod
    def ne(cls, left, right):
        return cls(left=left, right=right, op='!=')


class Program(Node):
    """
    Collection of statements
    """

    def __init__(self, *statements):
        super().__init__(statements=tuple(statements))
        for stmt in self.statements:
            assert isinstance(stmt, Statement), f'{stmt} is not a statement'


class Clause(Node):
    """
    Example: LBRACE statements RBRACE
    Should work for if statements, function definitions too maybe?
    """

    def __init__(self, *statements):
        super().__init__(statements=list(statements))
        for stmt in self.statements:
            assert isinstance(stmt, Statement), f'{stmt} is not a statement'


class IfStatement(Statement):
    """
    IF expr LBRACE statements RBRACE [ ELSE LBRACE statements RBRACE ]
    """

    def __init__(self, condition, consequent, alternative=None):
        assert isinstance(condition, Expression)
        assert isinstance(consequent, Clause)
        if alternative is not None:
            assert isinstance(alternative, Clause)
        super().__init__(condition=condition, consequent=consequent, alternative=alternative)


class Assignment(Statement):
    """
    location ASSIGN expression SEMI
    """

    def __init__(self, location, value):
        assert isinstance(location, Location)
        assert isinstance(value, Expression)
        super().__init__(location=location, value=value)


class AugmentedAssignment(Assignment):
    """
    assignment with an operation, e.g. += *=, etc.
    """


class WhileLoop(Statement):
    def __init__(self, condition, body):
        assert isinstance(condition, Expression)
        assert isinstance(body, Clause)
        super().__init__(condition=condition, body=body)


class ForLoop(Statement):
    """
    FOR location{additional_locations} IN expr
    """

    def __init__(self, location, expression):
        assert isinstance(location, Location)
        assert isinstance(expression, Expression)
        super().__init__(location=location)


class Parameter(Node):
    def __init__(self, name, type):
        assert isinstance(name, str)
        assert isinstance(type, str)
        super().__init__(name=name, type=type)


class FunctionDefinition(Definition):
    def __init__(self, name, parameters, rtype, body):
        assert isinstance(name, str)
        assert parameters is None or isinstance(parameters, Iterable)
        parameters = tuple(parameters) if parameters else tuple()
        assert all(isinstance(param, Parameter) for param in parameters)
        assert rtype is None or isinstance(rtype, str)
        assert isinstance(body, Clause)
        super().__init__(name=name, parameters=parameters, rtype=rtype, body=body)


class ReturnStatement(Statement):
    def __init__(self, expression):
        assert isinstance(expression, Expression)
        super().__init__(expression=expression)


class FunctionCall(ExpressionStatement):
    def __init__(self, name, arguments):
        assert isinstance(name, str)  # can functions be stored at locations?
        assert arguments is None or isinstance(arguments, Iterable)
        arguments = tuple(arguments) if arguments else tuple()
        assert all(isinstance(arg, Expression) for arg in arguments)
        super().__init__(name=name, arguments=arguments)


class BreakStatement(Statement):
    ...


class ContinueStatement(Statement):
    ...


class Grouping(Expression):
    """
    LPAREN expression RPAREN
    """

    def __init__(self, expression):
        assert isinstance(expression, Expression)
        super().__init__(expression=expression)


from functools import lru_cache


@lru_cache(maxsize=1024)
def black_format_code(source):
    import black

    kwargs = {
        'line_length': 120,
    }
    reformatted_source = black.format_file_contents(
        source, fast=True, mode=black.FileMode(**kwargs)
    )
    return reformatted_source
