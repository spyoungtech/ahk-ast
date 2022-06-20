import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
)

from ahk_ast.model import *

model = Program(
    HotkeyDefinition(
        hotkey=Hotkey(keyname='n', modifiers='#'),
        action=Block(FunctionCall(name='Run', arguments=[DoubleQuotedString(value='notepad')])),
    ),
)
