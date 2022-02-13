from typing import Any
from typing import TYPE_CHECKING
from typing import Union


class AHKAstBaseException(Exception):
    ...


class AHKDecodeError(ValueError, AHKAstBaseException):
    def __init__(self, msg: str, doc: str, pos: int):
        lineno = doc.count('\n', 0, pos) + 1
        colno = pos - doc.rfind('\n', 0, pos)
        errmsg = '%s: line %d column %d (char %d)' % (msg, lineno, colno, pos)
        ValueError.__init__(self, errmsg)
        self.msg = msg
        self.doc = doc
        self.pos = pos
        self.lineno = lineno
        self.colno = colno

    def __reduce__(self):  # type: ignore
        return self.__class__, (self.msg, self.doc, self.pos)


class AHKTokenizeError(AHKDecodeError):
    def __init__(self, msg: str, token: Any):
        lineno = getattr(token, 'lineno', 0)
        index = getattr(token, 'index', 0)
        doc = getattr(token, 'doc', None)
        self.token = token
        self.index = index
        if token and doc:
            errmsg = f'{msg} in or near token {token.type} at'
            super().__init__(errmsg, doc, index)
        else:
            ValueError.__init__(self, msg)
            self.msg = msg
            self.lineno = lineno

    def __reduce__(self):  # type: ignore
        return self.__class__, (self.msg, self.token)


class ParsingException(AHKDecodeError):
    def __init__(self, msg: str, token: Any):
        lineno = getattr(token, 'lineno', 0)
        index = getattr(token, 'index', 0)
        doc = getattr(token, 'doc', None)
        self.token = token
        self.index = index
        if token and doc:
            errmsg = f'{msg} in or near token {token.type} at'
            super().__init__(errmsg, doc, index)
        else:
            ValueError.__init__(self, msg)
            self.msg = msg
            self.lineno = lineno

    def __reduce__(self):  # type: ignore
        return self.__class__, (self.msg, self.token)


class InvalidHotkeyException(ParsingException):
    ...
