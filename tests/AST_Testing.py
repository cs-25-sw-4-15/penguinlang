# https://docs.pytest.org/en/stable/getting-started.html
import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from antlr4 import InputStream, CommonTokenStream
from src.generated.penguinLexer import penguinLexer
from src.generated.penguinParser import penguinParser
from src.ast_generator import ASTGenerator

from src.ast_classes import (
    Program, Declaration, Assignment, Initialization, ListInitialization,
    Conditional, Loop, Return, ProcedureCallStatement, BinaryOp, UnaryOp,
    IntegerLiteral, StringLiteral, ProcedureCall, Variable, ListAccess, AttributeAccess
)

def build_ast(source_code):
    """Build an AST from source code."""
    input_stream = InputStream(source_code)
    lexer = penguinLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = penguinParser(token_stream)
    parse_tree = parser.program()
    
    visitor = ASTGenerator()
    return visitor.visit(parse_tree)


# Fixture for AST generator
@pytest.fixture
def ast_generator():
    """Fixture providing a fresh AST generator."""
    return ASTGenerator()



#######################
# Basic Structure Tests
#######################


def test_empty_program():
    ast = build_ast("")
    assert isinstance(ast, Program)
    assert len(ast.statements) == 0


#######################
# Declaration Tests
#######################

def test_declaration():
    ast = build_ast("int x;")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Declaration)
    assert ast.statements[0].var_type == "int"
    assert ast.statements[0].name == "x"

def test_multiple_declarations():
    ast = build_ast("int x; string y;")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 2
    assert isinstance(ast.statements[0], Declaration)
    assert isinstance(ast.statements[1], Declaration)
    assert ast.statements[0].var_type == "int"
    assert ast.statements[0].name == "x"
    assert ast.statements[1].var_type == "string"
    assert ast.statements[1].name == "y"

#######################
# Assignment Tests
#######################
def test_simple_assignment():
    ast = build_ast("x = 42;")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Assignment)
    assert isinstance(ast.statements[0].target, Variable)
    assert ast.statements[0].target.name == "x"
    assert isinstance(ast.statements[0].value, IntegerLiteral)
    assert ast.statements[0].value.value == 42

def test_list_assignment():
    ast = build_ast("x[0] = 42;")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Assignment)
    assert isinstance(ast.statements[0].target, ListAccess)
    assert isinstance(ast.statements[0].target.name, Variable)
    assert ast.statements[0].target.name.name == "x"
    assert isinstance(ast.statements[0].target.indices[0], IntegerLiteral)
    assert ast.statements[0].target.indices[0].value == 0
    assert isinstance(ast.statements[0].value, IntegerLiteral)
    assert ast.statements[0].value.value == 42

#######################
# Initialization Tests
#######################
def test_simple_initialization():
    ast = build_ast("int x = 42;")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Initialization)
    assert ast.statements[0].var_type == "int"
    assert ast.statements[0].name == "x"
    assert isinstance(ast.statements[0].value, IntegerLiteral)
    assert ast.statements[0].value.value == 42

def test_list_initialization():
    ast = build_ast("x = [1, 2, 3];")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], ListInitialization)
    assert ast.statements[0].name == "x"
    assert len(ast.statements[0].values) == 3
    assert all(isinstance(val, IntegerLiteral) for val in ast.statements[0].values)
    assert [val.value for val in ast.statements[0].values] == [1, 2, 3]


#######################
# Binary Expression Tests
#######################

#######################
# Unary Expression Tests
#######################

#######################
# Literal Tests
#######################

#######################
# Conditional Tests
#######################

#######################
# Loop Tests
#######################

#######################
# Procedure Tests
#######################

#######################
# List Tests
#######################

#######################
# Dot Notation Tests
#######################

#######################
# Complex Tests
#######################