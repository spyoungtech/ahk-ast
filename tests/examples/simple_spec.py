import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
)

from ahk_ast.model import *

model = Program(
    Assignment(location=Identifier(name='a'), value=Integer(value=1)),
    Assignment(
        location=Identifier(name='b'),
        value=BinOp(op='+', left=Identifier(name='a'), right=Integer(value=1)),
    ),
    FunctionCall(name='MsgBox', arguments=[Identifier(name='b')]),
)
