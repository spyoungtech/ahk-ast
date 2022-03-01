import json
import os
import sys
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec
from importlib.util import spec_from_file_location
from textwrap import dedent

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')))
from ahk_ast import parser
from ahk_ast.model import *
from ahk_ast.tokenizer import tokenize

tests_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'examples'))


@pytest.mark.parametrize('op', argvalues=[('+',), ('-',), ('*',), ('/',), ('//',), ('**',)])
def test_math_binop(op):
    op = op[0]
    script = dedent(
        f"""\
        a := 1 {op} 1
        """
    )
    expected = Program(
        Assignment(
            location=Identifier(name='a'),
            value=BinOp(left=Integer(value=1), right=Integer(value=1), op=op),
        )
    )
    model = parser.parse(script)
    assert model == expected
