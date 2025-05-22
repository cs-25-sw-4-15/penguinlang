import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class UnknownExpressionTypeError(Exception):
    pass


class UnknownValueTypeError(Exception):
    pass


class UnknowninitializationTypeError(Exception):
    pass


class UnknownLiteralTypeError(Exception):
    pass


""" Type errors """


class TypeError(Exception):
    pass


class TypeMismatchError(TypeError):
    pass


class UndeclaredVariableError(TypeError):
    pass


class DuplicateDeclarationError(TypeError):
    pass


class InvalidTypeError(TypeError):
    pass


class InvalidAttributeError(TypeError):
    pass
