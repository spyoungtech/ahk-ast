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


def test_assignment_literal():
    script = dedent(
        """\
        a := 1
        b := "Hello World!\""""
    )
    expected = Program(
        Assignment(location=Identifier(name='a'), value=Integer(value=1)),
        Assignment(location=Identifier(name='b'), value=DoubleQuotedString(value='Hello World!')),
    )
    model = parser.parse(script)
    assert model == expected


def test_two_statements():
    script = dedent(
        """\
        a := 1
        b := 1"""
    )
    expected = Program(
        Assignment(location=Identifier(name='a'), value=Integer(value=1)),
        Assignment(location=Identifier(name='b'), value=Integer(value=1)),
    )
    model = parser.parse(script)
    assert model == expected


def test_trailing_line_ws():
    script = 'a := 1\n  \n   \n\n  \n'
    for t in tokenize(script):
        print(t)
    expected = Program(
        Assignment(location=Identifier(name='a'), value=Integer(value=1)),
    )
    model = parser.parse(script)
    assert model == expected


def test_leading_lines_ws():
    script = '\n  \n\n   \na := 1'
    for t in tokenize(script):
        print(t)
    expected = Program(
        Assignment(location=Identifier(name='a'), value=Integer(value=1)),
    )
    model = parser.parse(script)
    assert model == expected
