# ahk-ast

![example workflow](https://github.com/spyoungtech/ahk-ast/actions/workflows/unittests.yaml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/spyoungtech/ahk-ast/badge.svg?branch=main)](https://coveralls.io/github/spyoungtech/ahk-ast?branch=main)



This is an attempt at implementing a parser for AutoHotkey using a LALR(1) parser generator (provided by `sly`).
Ultimately, the ability to parse AHK syntax programmatically will help in the production of other tools, such as
linters, code formatters, compilers, and more.


Goals:

- Define a formal grammar for AutoHotkey
- Ability to tokenize AutoHotkey code
- Ability to generate an abstract syntax tree (AST) from AutoHotkey code


Extended goals:

- Ability to reproduce source code from AST models ("round-tripping")
- Ability to modify AST nodes and reproduce source code
- Ability to preserve comments in round-trip editing.



However, it's unclear how successful this endeavor will be, or if it can be successful at all. If a LALR grammar cannot
be established, then this project will likely remain incomplete.

# Usage


## Tokenizing

```bash
python -m ahk_ast.tokenizer myfile.ahk
```

## Parsing

```python
import ahk_ast
ahk_source = """\
a := 1
b := a + 1

MsgBox b
"""

ahk_ast.parse(ahk_source)
# Program(
#     statements=(
#         Assignment(location=Identifier(name="a"), value=Integer(value=1)),
#         Assignment(
#             location=Identifier(name="b"), value=BinOp(op="+", left=Identifier(name="a"), right=Integer(value=1))
#         ),
#         FunctionCall(name="MsgBox", arguments=(Identifier(name="b"),)),
#     )
# )

```

# Status

This project is in its very early phases. Almost none of the language syntax is fully implemented into the parser.
The tokenizer has most the tokens that exist for AHK, but is still very much subject to change.
