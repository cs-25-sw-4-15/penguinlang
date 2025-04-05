"""AST Generator for Penguin Language 

Generates AST by walking with the ANTLR4 generated visitor pattern 
and self-made AST classes on a CFT.
"""


# Generated modules
from generated.penguinParser import penguinParser
from generated.penguinVisitor import penguinVisitor

# Custom modules
from ast_classes import Program, \
    Declaration, Assignment, Initialization, ListInitialization, If, Loop, Return, ProcedureCallStatement, \
    UnaryOp, IntegerLiteral, StringLiteral, Variable, ListAccess, AttributeAccess, \
    ProcedureDef


class ASTGenerator(penguinVisitor):
    """Converts an ANTLR parse tree into an AST."""

    pass