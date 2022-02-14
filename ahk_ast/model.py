from collections.abc import Iterable
from types import SimpleNamespace as _SimpleNamespace
from typing import Optional
from typing import Sequence
from typing import Union


class Node(_SimpleNamespace):
    def __eq__(self, other: 'Node') -> bool:  # type: ignore[override]
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

    def __repr__(self) -> str:
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
        except ImportError:
            # Just in case you don't have `black` installed :-)
            return rep
        except Exception as e:
            print('WARN: Unexpected error formatting code ', e)
            return rep


class Statement(Node):
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

    def __init__(self, location: Location, fieldname: str, nested: bool = False):
        assert isinstance(
            location, Location
        ), f'Expected Location. got {type(location)} {repr(location)}'
        assert isinstance(fieldname, str), f'Expected str. got {type(fieldname)}'
        super().__init__(location=location, fieldname=fieldname, nested=nested)


class Integer(Expression):
    """
    Example: 42
    """

    def __init__(self, value: int):
        assert isinstance(value, int)
        super().__init__(value=value)


class Float(Expression):
    """
    Example: 42.0
    """

    def __init__(self, value: float):
        assert isinstance(value, float)
        super().__init__(value=value)


class Bool(Expression):
    def __init__(self, value: bool):
        assert isinstance(value, bool)
        super().__init__(value=value)


class UnaryOp(Expression):
    def __init__(self, op: str, operand: Expression):
        assert isinstance(op, str)
        assert op in ('+', '-', '!'), f'Invalid Unary operand: {op}'
        assert isinstance(operand, Expression)
        super().__init__(op=op, operand=operand)


class Identifier(Location):
    def __init__(self, name: str):
        assert isinstance(name, str)
        super().__init__(name=name)


class BinOp(Expression):
    """
    Example: left + right
    """

    def __init__(self, op: str, left: Expression, right: Expression):
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


class Compare(BinOp):
    """
    ==, !=, <, >, <=, >=
    Comparisons operations always end up being Bools
    """

    @classmethod
    def lt(cls, left: Expression, right: Expression) -> 'Compare':
        return cls(left=left, right=right, op='<')

    @classmethod
    def lte(cls, left: Expression, right: Expression) -> 'Compare':
        return cls(left=left, right=right, op='<=')

    @classmethod
    def gt(cls, left: Expression, right: Expression) -> 'Compare':
        return cls(left=left, right=right, op='>')

    @classmethod
    def gte(cls, left: Expression, right: Expression) -> 'Compare':
        return cls(left=left, right=right, op='>=')

    @classmethod
    def eq(cls, left: Expression, right: Expression) -> 'Compare':
        return cls(left=left, right=right, op='==')

    @classmethod
    def ne(cls, left: Expression, right: Expression) -> 'Compare':
        return cls(left=left, right=right, op='!=')


class Program(Node):
    """
    Collection of statements
    """

    def __init__(self, *statements: Statement):
        super().__init__(statements=tuple(statements))
        for stmt in self.statements:
            assert isinstance(stmt, Statement), f'{stmt} is not a statement'


class Block(ExpressionStatement):
    """
    Example: LBRACE statements RBRACE
    Should work for if statements, function definitions too maybe?
    """

    def __init__(self, *statements: Statement):
        super().__init__(statements=list(statements))
        for stmt in self.statements:
            assert isinstance(stmt, Statement), f'{stmt} is not a statement'


class IfStatement(Statement):
    """
    IF expr LBRACE statements RBRACE [ ELSE LBRACE statements RBRACE ]
    """

    def __init__(
        self, condition: Expression, consequent: Block, alternative: Optional[Block] = None
    ):
        assert isinstance(condition, Expression)
        assert isinstance(consequent, Block)
        if alternative is not None:
            assert isinstance(alternative, Block)
        super().__init__(condition=condition, consequent=consequent, alternative=alternative)


class Assignment(Statement):
    """
    location ASSIGN expression SEMI
    """

    def __init__(self, location: Location, value: Expression):
        assert isinstance(location, Location)
        assert isinstance(value, Expression)
        super().__init__(location=location, value=value)


class AugmentedAssignment(Assignment):
    """
    assignment with an operation, e.g. += *=, etc.
    """


class WhileLoop(Statement):
    def __init__(self, condition: Expression, body: Block):
        assert isinstance(condition, Expression)
        assert isinstance(body, Block)
        super().__init__(condition=condition, body=body)


class ForLoop(Statement):
    """
    FOR location{additional_locations} IN expr
    """

    def __init__(self, location: Location, expression: Expression):
        assert isinstance(location, Location)
        assert isinstance(expression, Expression)
        super().__init__(location=location)


class Parameter(Node):
    def __init__(self, name: str, default_value: Optional[Expression] = None):
        assert isinstance(name, str)
        if default_value is not None:
            assert isinstance(default_value, Expression)
        super().__init__(name=name)


class FunctionDefinition(Statement):
    def __init__(self, name: str, parameters: Union[None, Sequence[Parameter]], body: Block):
        assert isinstance(name, str)
        assert parameters is None or isinstance(parameters, Iterable)
        parameters = tuple(parameters) if parameters else tuple()
        assert all(isinstance(param, Parameter) for param in parameters)
        assert isinstance(body, Block)
        super().__init__(name=name, parameters=parameters, body=body)


class ReturnStatement(Statement):
    def __init__(self, expression: Optional[Expression]):
        if expression is not None:
            assert isinstance(expression, Expression)
        super().__init__(expression=expression)


class FunctionCall(ExpressionStatement):
    def __init__(self, name: str, arguments: Union[Sequence[Expression], None]):
        assert isinstance(name, str)  # can functions be stored at locations?
        assert arguments is None or isinstance(arguments, Iterable)
        arguments = tuple(arguments) if arguments else tuple()
        assert all(isinstance(arg, Expression) for arg in arguments)
        super().__init__(name=name, arguments=arguments)


class FunctionCallStatement(FunctionCall):
    pass  # distinguish `MsgBox "foo"` from `MsgBox("foo")`


class Hotkey(Node):
    def __init__(self, keyname: str, modifiers: Optional[str] = None):
        assert isinstance(keyname, str)
        if modifiers is not None:
            assert isinstance(modifiers, str)
            assert modifiers  # can't be empty string
        super().__init__(keyname=keyname, modifiers=modifiers)


class HotkeyDefinition(Statement):
    def __init__(self, hotkey: Hotkey, action: Statement, second_hotkey: Optional[Hotkey] = None):
        assert isinstance(hotkey, Hotkey)
        assert isinstance(action, Statement)
        if second_hotkey is not None:
            assert isinstance(second_hotkey, Hotkey)
        super().__init__(hotkey=hotkey, action=action, second_hotkey=second_hotkey)


class BreakStatement(Statement):
    ...


class ContinueStatement(Statement):
    ...


class Grouping(Expression):
    """
    LPAREN expression RPAREN
    """

    def __init__(self, expression: Expression):
        assert isinstance(expression, Expression)
        super().__init__(expression=expression)


class String(Expression):
    def __init__(self, value: str):
        assert isinstance(value, str)
        super().__init__(value=value)


class DoubleQuotedString(String):
    ...


class SingleQuotedString(String):
    ...


from functools import lru_cache


@lru_cache(maxsize=1024)
def black_format_code(source: str) -> str:
    import black

    reformatted_source = black.format_file_contents(
        source, fast=True, mode=black.FileMode(line_length=120)
    )
    return reformatted_source
