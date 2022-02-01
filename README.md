# ahk-ast

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

TBD
