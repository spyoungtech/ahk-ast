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


def test_function_call_statement():
    script = 'MsgBox "Hello AutoHotkey!"'
    expected = Program(
        FunctionCallStatement(
            func_location=Identifier(name='MsgBox'),
            arguments=[DoubleQuotedString(value='Hello AutoHotkey!')],
        )
    )
    for t in tokenize(script):
        print(t)
    model = parser.parse(script)
    assert model == expected


def test_function_call_statement_no_arguments():
    script = 'MsgBox'
    expected = Program(
        FunctionCallStatement(func_location=Identifier(name='MsgBox'), arguments=None)
    )
    for t in tokenize(script):
        print(t)
    model = parser.parse(script)
    assert model == expected


def test_function_call_statement_multiple_arguments():
    script = 'MsgBox "Hello", "World"'
    expected = Program(
        FunctionCallStatement(
            func_location=Identifier(name='MsgBox'),
            arguments=[DoubleQuotedString(value='Hello'), DoubleQuotedString(value='World')],
        )
    )
    for t in tokenize(script):
        print(t)
    model = parser.parse(script)
    assert model == expected


def test_function_call():
    script = 'MsgBox("Hello AutoHotkey!")'
    expected = Program(
        FunctionCall(
            func_location=Identifier(name='MsgBox'),
            arguments=[DoubleQuotedString(value='Hello AutoHotkey!')],
        )
    )
    for t in tokenize(script):
        print(t)
    model = parser.parse(script)
    assert model == expected


def test_function_call_no_arguments():
    script = 'MsgBox()'
    expected = Program(
        FunctionCallStatement(func_location=Identifier(name='MsgBox'), arguments=None)
    )
    for t in tokenize(script):
        print(t)
    model = parser.parse(script)
    assert model == expected


def test_function_call_multiple_arguments():
    script = 'MsgBox("Hello", "World")'
    expected = Program(
        FunctionCallStatement(
            func_location=Identifier(name='MsgBox'),
            arguments=[DoubleQuotedString(value='Hello'), DoubleQuotedString(value='World')],
        )
    )
    for t in tokenize(script):
        print(t)
    model = parser.parse(script)
    assert model == expected


def test_function_call_statement_tailing_comma():
    script = 'MsgBox "Hello", "World",,'
    expected = Program(
        FunctionCallStatement(
            func_location=Identifier(name='MsgBox'),
            arguments=[DoubleQuotedString(value='Hello'), DoubleQuotedString(value='World')],
        )
    )
    for t in tokenize(script):
        print(t)
    model = parser.parse(script)
    assert model == expected
