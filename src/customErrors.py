"""Definitions of error classes used in  the project."""

""" AST errors """

import sys
import os
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
    """Base class for type errors."""
    pass


class TypeMismatchError(TypeError):
    """Error for when types don't match."""
    pass


class UndeclaredVariableError(TypeError):
    """Error for when a variable is used but not declared."""
    pass


class DuplicateDeclarationError(TypeError):
    """Error for when a variable is declared multiple times."""
    pass


class InvalidTypeError(TypeError):
    """Error for when an invalid type is used."""
    pass


class InvalidAttributeError(TypeError):
    """Error for when an invalid attribute is used."""
    pass
