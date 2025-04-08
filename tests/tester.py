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
    Conditional, Loop, Return, ProcedureCallStatement, ProcedureDef, BinaryOp, UnaryOp,
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

def test_binary_expression():
    ast = build_ast("x = a + b;")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Assignment)
    assert isinstance(ast.statements[0].value, BinaryOp)
    assert ast.statements[0].value.op == "+"
    assert isinstance(ast.statements[0].value.left, Variable)
    assert ast.statements[0].value.left.name == "a"
    assert isinstance(ast.statements[0].value.right, Variable)
    assert ast.statements[0].value.right.name == "b"

def test_complex_binary_expression():
    ast = build_ast("x = a + b * c;")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Assignment)
    assert isinstance(ast.statements[0].value, BinaryOp)
    assert ast.statements[0].value.op == "+"
    assert isinstance(ast.statements[0].value.left, Variable)
    assert ast.statements[0].value.left.name == "a"
    assert isinstance(ast.statements[0].value.right, BinaryOp)
    assert ast.statements[0].value.right.op == "*"
    assert isinstance(ast.statements[0].value.right.left, Variable)
    assert ast.statements[0].value.right.left.name == "b"
    assert isinstance(ast.statements[0].value.right.right, Variable)
    assert ast.statements[0].value.right.right.name == "c"

def test_parenthesized_expression():
    ast = build_ast("x = (a + b) * c;")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Assignment)
    assert isinstance(ast.statements[0].value, BinaryOp)
    assert ast.statements[0].value.op == "*"
    assert isinstance(ast.statements[0].value.left, BinaryOp)
    assert ast.statements[0].value.left.op == "+"
    assert isinstance(ast.statements[0].value.right, Variable)
    assert ast.statements[0].value.right.name == "c"
    
#######################
# Unary Expression Tests
#######################
def test_unary_expression():
    ast = build_ast("x = -a;")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Assignment)
    assert isinstance(ast.statements[0].value, UnaryOp)
    assert ast.statements[0].value.op == "-"
    assert isinstance(ast.statements[0].value.operand, Variable)
    assert ast.statements[0].value.operand.name == "a"

#######################
# Literal Tests
#######################

def test_integer_literal():
    """Test integer literal AST construction."""
    ast = build_ast("x = 42;")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Assignment)
    assert isinstance(ast.statements[0].value, IntegerLiteral)
    assert ast.statements[0].value.value == 42

def test_hex_literal():
    """Test hexadecimal literal AST construction."""
    ast = build_ast("x = 0x2A;")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Assignment)
    assert isinstance(ast.statements[0].value, IntegerLiteral)
    assert ast.statements[0].value.value == 42  # 0x2A = 42

def test_binary_literal():
    """Test binary literal AST construction."""
    ast = build_ast("x = 0b101010;")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Assignment)
    assert isinstance(ast.statements[0].value, IntegerLiteral)
    assert ast.statements[0].value.value == 42  # 0b101010 = 42

def test_string_literal():
    """Test string literal AST construction."""
    ast = build_ast("x = \"hello\";")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Assignment)
    assert isinstance(ast.statements[0].value, StringLiteral)
    assert ast.statements[0].value.value == "\"hello\""  # Note: includes quotes

#######################
# Conditional Tests
#######################

def test_conditional_statement():
    ast = build_ast("if (x > 0) { y = 1; }")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Conditional)
    assert isinstance(ast.statements[0].condition, BinaryOp)
    assert ast.statements[0].condition.op == ">"
    assert isinstance(ast.statements[0].condition.left, Variable)
    assert ast.statements[0].condition.left.name == "x"
    assert isinstance(ast.statements[0].condition.right, IntegerLiteral)
    assert ast.statements[0].condition.right.value == 0
    assert len(ast.statements[0].then_body) == 1
    assert isinstance(ast.statements[0].then_body[0], Assignment)
    assert len(ast.statements[0].else_body) == 0  # No else body

def test_conditional_with_else():
    ast = build_ast("if (x > 0) { y = 1; } else { y = 2; }")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Conditional)
    assert isinstance(ast.statements[0].condition, BinaryOp)
    assert len(ast.statements[0].then_body) == 1
    assert isinstance(ast.statements[0].then_body[0], Assignment)
    assert len(ast.statements[0].else_body) == 1
    assert isinstance(ast.statements[0].else_body[0], Assignment)
    assert isinstance(ast.statements[0].else_body[0].value, IntegerLiteral)
    assert ast.statements[0].else_body[0].value.value == 2

#######################
# Loop Tests
#######################

def test_loop_statement():
    ast = build_ast("while (i < 10) { i = i + 1; }")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Loop)
    assert isinstance(ast.statements[0].condition, BinaryOp)
    assert ast.statements[0].condition.op == "<"
    assert isinstance(ast.statements[0].condition.left, Variable)
    assert ast.statements[0].condition.left.name == "i"
    assert isinstance(ast.statements[0].condition.right, IntegerLiteral)
    assert ast.statements[0].condition.right.value == 10
    assert len(ast.statements[0].body) == 1
    assert isinstance(ast.statements[0].body[0], Assignment)
    assert isinstance(ast.statements[0].body[0].value, BinaryOp)
    assert ast.statements[0].body[0].value.op == "+"

#######################
# Procedure Tests
#######################

def test_procedure_call():
    ast = build_ast("print(42);")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], ProcedureCallStatement)
    assert isinstance(ast.statements[0].call, ProcedureCall)
    assert isinstance(ast.statements[0].call.name, Variable)
    assert ast.statements[0].call.name.name == "print"
    assert len(ast.statements[0].call.args) == 1
    assert isinstance(ast.statements[0].call.args[0], IntegerLiteral)
    assert ast.statements[0].call.args[0].value == 42

def test_procedure_call_multiple_args():
    ast = build_ast("print(42, \"hello\", x);")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], ProcedureCallStatement)
    assert isinstance(ast.statements[0].call, ProcedureCall)
    assert len(ast.statements[0].call.args) == 3
    assert isinstance(ast.statements[0].call.args[0], IntegerLiteral)
    assert isinstance(ast.statements[0].call.args[1], StringLiteral)
    assert isinstance(ast.statements[0].call.args[2], Variable)

def test_procedure_definition():
    ast = build_ast("int add(int a, int b) { return a + b; }")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], ProcedureDef)
    assert ast.statements[0].return_type == "int"
    assert ast.statements[0].name == "add"
    assert len(ast.statements[0].params) == 2
    assert ast.statements[0].params[0] == ("int", "a")
    assert ast.statements[0].params[1] == ("int", "b")
    assert len(ast.statements[0].body) == 1
    assert isinstance(ast.statements[0].body[0], Return)
    assert isinstance(ast.statements[0].body[0].value, BinaryOp)
    assert ast.statements[0].body[0].value.op == "+"

def test_void_procedure_definition():
    ast = build_ast("void printHello() { print(\"hello\"); }")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], ProcedureDef)
    assert ast.statements[0].return_type == "void"
    assert ast.statements[0].name == "printHello"
    assert len(ast.statements[0].params) == 0
    assert len(ast.statements[0].body) == 1
    assert isinstance(ast.statements[0].body[0], ProcedureCallStatement)

def test_return_statement():
    ast = build_ast("int foo() { return 42; }")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], ProcedureDef)
    assert len(ast.statements[0].body) == 1
    assert isinstance(ast.statements[0].body[0], Return)
    assert isinstance(ast.statements[0].body[0].value, IntegerLiteral)
    assert ast.statements[0].body[0].value.value == 42

#######################
# List Tests
#######################

def test_list_access():
    """Test list access AST construction."""
    ast = build_ast("x = arr[i];")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Assignment)
    assert isinstance(ast.statements[0].value, ListAccess)
    assert isinstance(ast.statements[0].value.name, Variable)
    assert ast.statements[0].value.name.name == "arr"
    assert len(ast.statements[0].value.indices) == 1
    assert isinstance(ast.statements[0].value.indices[0], Variable)
    assert ast.statements[0].value.indices[0].name == "i"

def test_nested_list_access():
    """Test nested list access AST construction."""
    ast = build_ast("x = arr[i][j];")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Assignment)
    assert isinstance(ast.statements[0].value, ListAccess)
    assert isinstance(ast.statements[0].value.name, ListAccess)
    assert isinstance(ast.statements[0].value.name.name, Variable)
    assert ast.statements[0].value.name.name.name == "arr"
    assert len(ast.statements[0].value.indices) == 1
    assert isinstance(ast.statements[0].value.indices[0], Variable)
    assert ast.statements[0].value.indices[0].name == "j"

#######################
# Dot Notation Tests
#######################

def test_attribute_access():
    """Test attribute access AST construction."""
    ast = build_ast("x = obj.attr;")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Assignment)
    assert isinstance(ast.statements[0].value, AttributeAccess)
    assert isinstance(ast.statements[0].value.name, Variable)
    assert ast.statements[0].value.name.name == "obj"
    assert ast.statements[0].value.attribute == "attr"

def test_chained_attribute_access():
    """Test chained attribute access AST construction."""
    ast = build_ast("x = obj.attr1.attr2;")
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Assignment)
    assert isinstance(ast.statements[0].value, AttributeAccess)
    assert isinstance(ast.statements[0].value.name, AttributeAccess)
    assert isinstance(ast.statements[0].value.name.name, Variable)
    assert ast.statements[0].value.name.name.name == "obj"
    assert ast.statements[0].value.name.attribute == "attr1"
    assert ast.statements[0].value.attribute == "attr2"

#######################
# Complex Tests
#######################

def test_complex_nested_structure():
    """Test complex nested structure AST construction."""
    code = """
    if (x > 0) {
        while (i < 10) {
            i = i + 1;
            if (i == 5) {
                print(i);
            }
        }
    } else {
        print("x is not positive");
    }
    """
    ast = build_ast(code)
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Conditional)
    assert isinstance(ast.statements[0].condition, BinaryOp)
    assert len(ast.statements[0].then_body) == 1
    assert isinstance(ast.statements[0].then_body[0], Loop)
    assert len(ast.statements[0].then_body[0].body) == 2
    assert isinstance(ast.statements[0].then_body[0].body[1], Conditional)
    assert len(ast.statements[0].else_body) == 1
    assert isinstance(ast.statements[0].else_body[0], ProcedureCallStatement)

#######################
# Error Tests
#######################

def test_error_handling():
    with pytest.raises(Exception):  # Replace with specific exception class if known
        build_ast("int x = ;")  # Missing expression
