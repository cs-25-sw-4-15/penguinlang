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
# Declaration Tests
#######################

def test_declaration():
    ast = build_ast("int x;")
    assert isinstance(type(ast.statements[0]), type(Declaration))
    assert len(ast.statements) == 1
    assert ast.statements[0].var_type == "int"
    assert ast.statements[0].name == "x"

def test_multiple_declarations():
    ast = build_ast("int x; int y;")
    
    assert len(ast.statements) == 2
    assert isinstance(type(ast.statements[0]), type(Declaration))
    assert isinstance(type(ast.statements[1]), type(Declaration))
    assert ast.statements[0].var_type == "int"
    assert ast.statements[0].name == "x"
    assert ast.statements[1].var_type == "int"
    assert ast.statements[1].name == "y"

#######################
# Assignment Tests
#######################
def test_simple_assignment():
    ast = build_ast("x = 42;")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(Assignment))
    assert isinstance(type(ast.statements[0].target), type(Variable))
    assert ast.statements[0].target.name == "x"
    assert isinstance(type(ast.statements[0].value), type(IntegerLiteral))
    assert ast.statements[0].value.value == 42

def test_list_assignment():
    ast = build_ast("x[0] = 42;")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(Assignment))
    assert isinstance(type(ast.statements[0].target), type(ListAccess))
    assert isinstance(type(ast.statements[0].target.name), type(Variable))
    assert ast.statements[0].target.name == "x"
    assert isinstance(type(ast.statements[0].target.indices), type(IntegerLiteral))
    assert ast.statements[0].target.indices.value == 0
    assert isinstance(type(ast.statements[0].value), type(IntegerLiteral))
    assert ast.statements[0].value.value == 42


#######################
# Initialization Tests
#######################
def test_simple_initialization():
    ast = build_ast("int x = 42;")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(Initialization))
    assert ast.statements[0].var_type == "int"
    assert ast.statements[0].name == "x"
    assert isinstance(type(ast.statements[0].value), type(IntegerLiteral))
    assert ast.statements[0].value.value == 42

def test_list_initialization():
    ast = build_ast("list x = [1, 2, 3];")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(ListInitialization))
    assert ast.statements[0].name == "x"
    assert len(ast.statements[0].values) == 3
    assert all(isinstance(type(val), type(IntegerLiteral)) for val in ast.statements[0].values)
    assert [val.value for val in ast.statements[0].values] == [1, 2, 3]


#######################
# Binary Expression Tests
#######################

def test_binary_expression():
    ast = build_ast("x = a + b;")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(Assignment))
    assert isinstance(type(ast.statements[0].value), type(BinaryOp))
    assert ast.statements[0].value.op == "+"
    assert isinstance(type(ast.statements[0].value.left), type(Variable))
    assert ast.statements[0].value.left.name == "a"
    assert isinstance(type(ast.statements[0].value.right), type(Variable))
    assert ast.statements[0].value.right.name == "b"

def test_complex_binary_expression():
    ast = build_ast("x = a + b * c;")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(Assignment))
    assert isinstance(type(ast.statements[0].value), type(BinaryOp))
    assert ast.statements[0].value.op == "+"
    assert isinstance(type(ast.statements[0].value.left), type(Variable))
    assert ast.statements[0].value.left.name == "a"
    assert isinstance(type(ast.statements[0].value.right), type(BinaryOp))
    assert ast.statements[0].value.right.op == "*"
    assert isinstance(type(ast.statements[0].value.right.left), type(Variable))
    assert ast.statements[0].value.right.left.name == "b"
    assert isinstance(type(ast.statements[0].value.right.right), type(Variable))
    assert ast.statements[0].value.right.right.name == "c"

def test_parenthesized_expression():
    ast = build_ast("x = (a + b) * c;")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(Assignment))
    assert isinstance(type(ast.statements[0].value), type(BinaryOp))
    assert ast.statements[0].value.op == "*"
    assert isinstance(type(ast.statements[0].value.left), type(BinaryOp))
    assert ast.statements[0].value.left.op == "+"
    assert isinstance(type(ast.statements[0].value.right), type(Variable))
    assert ast.statements[0].value.right.name == "c"
    

#######################
# Literal Tests
#######################

def test_integer_literal():
    ast = build_ast("x = 42;")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(Assignment))
    assert isinstance(type(ast.statements[0].value), type(IntegerLiteral))
    assert ast.statements[0].value.value == 42

def test_hex_literal():
    ast = build_ast("x = 0x2A;")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(Assignment))
    assert isinstance(type(ast.statements[0].value), type(IntegerLiteral))
    assert ast.statements[0].value.value == 42  # 0x2A = 42

def test_binary_literal():
    """Test binary literal AST construction."""
    ast = build_ast("x = 0b101010;")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(Assignment))
    assert isinstance(type(ast.statements[0].value), type(IntegerLiteral))
    assert ast.statements[0].value.value == 42  # 0b101010 = 42

#######################
# Conditional Tests
#######################

def test_conditional_statement():
    ast = build_ast("if (x > 0) { y = 1; }")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(Conditional))
    assert isinstance(type(ast.statements[0].condition), type(BinaryOp))
    assert ast.statements[0].condition.op == ">"
    assert isinstance(type(ast.statements[0].condition.left), type(Variable))
    assert ast.statements[0].condition.left.name == "x"
    assert isinstance(type(ast.statements[0].condition.right), type(IntegerLiteral))
    assert ast.statements[0].condition.right.value == 0
    assert len(ast.statements[0].then_body) == 1
    assert isinstance(type(ast.statements[0].then_body[0]), type(Assignment))
    assert len(ast.statements[0].else_body) == 0  # No else body

def test_conditional_with_else():
    ast = build_ast("if (x > 0) { y = 1; } else { y = 2; }")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(Conditional))
    assert isinstance(type(ast.statements[0].condition), type(BinaryOp))
    assert len(ast.statements[0].then_body) == 1
    assert isinstance(type(ast.statements[0].then_body[0]), type(Assignment))
    assert len(ast.statements[0].else_body) == 1
    assert isinstance(type(ast.statements[0].else_body[0]), type(Assignment))
    assert isinstance(type(ast.statements[0].else_body[0].value), type(IntegerLiteral))
    assert ast.statements[0].else_body[0].value.value == 2

#######################
# Loop Tests
#######################

def test_loop_statement():
    ast = build_ast("loop (i < 10) { i = i + 1; }")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(Loop))
    assert isinstance(type(ast.statements[0].condition), type(BinaryOp))
    assert ast.statements[0].condition.op == "<"
    assert isinstance(type(ast.statements[0].condition.left), type(Variable))
    assert ast.statements[0].condition.left.name == "i"
    assert isinstance(type(ast.statements[0].condition.right), type(IntegerLiteral))
    assert ast.statements[0].condition.right.value == 10
    assert len(ast.statements[0].body) == 1
    assert isinstance(type(ast.statements[0].body[0]), type(Assignment))
    assert isinstance(type(ast.statements[0].body[0].value), type(BinaryOp))
    assert ast.statements[0].body[0].value.op == "+"

#######################
# Procedure Tests
#######################

def test_procedure_call():
    ast = build_ast("print(42);")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(ProcedureCallStatement))
    assert isinstance(type(ast.statements[0].call), type(ProcedureCall))
    assert isinstance(type(ast.statements[0].call.name), type(Variable))
    assert ast.statements[0].call.name.name == "print"
    assert len(ast.statements[0].call.args) == 1
    assert isinstance(type(ast.statements[0].call.args[0]), type(IntegerLiteral))
    assert ast.statements[0].call.args[0].value == 42

def test_procedure_call_multiple_args():
    ast = build_ast("print(42, x);")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(ProcedureCallStatement))
    assert isinstance(type(ast.statements[0].call), type(ProcedureCall))
    assert len(ast.statements[0].call.args) == 2
    assert isinstance(type(ast.statements[0].call.args[0]), type(IntegerLiteral))
    assert isinstance(type(ast.statements[0].call.args[1]), type(Variable))

def test_procedure_definition():
    ast = build_ast("procedure int add(int a, int b) { return a + b; }")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(ProcedureDef))
    assert ast.statements[0].return_type == "int"
    assert ast.statements[0].name == "add"
    assert len(ast.statements[0].params) == 2
    assert ast.statements[0].params[0] == ("a", "int")
    assert ast.statements[0].params[1] == ("b", "int")
    assert len(ast.statements[0].body) == 1
    assert isinstance(type(ast.statements[0].body[0]), type(Return))
    assert isinstance(type(ast.statements[0].body[0].value), type(BinaryOp))
    assert ast.statements[0].body[0].value.op == "+"

def test_void_procedure_definition():
    ast = build_ast("procedure printHello() { print(5); };")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(ProcedureDef))
    assert ast.statements[0].return_type == "void"
    assert ast.statements[0].name == "printHello"
    assert len(ast.statements[0].params) == 0
    assert len(ast.statements[0].body) == 1
    assert isinstance(type(ast.statements[0].body[0]), type(ProcedureCallStatement))

def test_return_statement():
    ast = build_ast("procedure int foo() { return 42; }")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(ProcedureDef))
    assert len(ast.statements[0].body) == 1
    assert isinstance(type(ast.statements[0].body[0]), type(Return))
    assert isinstance(type(ast.statements[0].body[0].value), type(IntegerLiteral))
    assert ast.statements[0].body[0].value.value == 42

#######################
# List Tests
#######################

def test_list_access():
    """Test list access AST construction."""
    ast = build_ast("x = arr[i];")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(Assignment))
    assert isinstance(type(ast.statements[0].value), type(ListAccess))
    assert isinstance(type(ast.statements[0].value.indices), type(Variable))
    assert ast.statements[0].value.name == "arr"
    assert isinstance(type(ast.statements[0].value.indices), type(Variable))
    assert ast.statements[0].value.indices.name == "i"

def test_nested_list_access():
    """Test nested list access AST construction."""
    ast = build_ast("x = arr[i][j];")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(Assignment))
    assert isinstance(type(ast.statements[0].value), type(ListAccess))
    assert isinstance(type(ast.statements[0].value.name), type(ListAccess))
    assert ast.statements[0].value.name.name == "arr"

#######################
# Dot Notation Tests
#######################

def test_attribute_access():
    """Test attribute access AST construction."""
    ast = build_ast("x = obj.attr;")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(Assignment))
    assert isinstance(type(ast.statements[0].value), type(AttributeAccess))
    assert isinstance(type(ast.statements[0].value.name), type(Variable))
    assert ast.statements[0].value.name.name == "obj"
    assert ast.statements[0].value.attribute == "attr"

def test_chained_attribute_access():
    """Test chained attribute access AST construction."""
    ast = build_ast("x = obj.attr1.attr2;")
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(Assignment))
    assert isinstance(type(ast.statements[0].value), type(AttributeAccess))
    assert isinstance(type(ast.statements[0].value.name), type(AttributeAccess))
    assert isinstance(type(ast.statements[0].value.name.name), type(Variable))
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
        loop (i < 10) {
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
    
    assert len(ast.statements) == 1
    assert isinstance(type(ast.statements[0]), type(Conditional))
    assert isinstance(type(ast.statements[0].condition), type(BinaryOp))
    assert len(ast.statements[0].then_body) == 1
    assert isinstance(type(ast.statements[0].then_body[0]), type(Loop))
    assert len(ast.statements[0].then_body[0].body) == 2
    assert isinstance(type(ast.statements[0].then_body[0].body[1]), type(Conditional))
    assert len(ast.statements[0].else_body) == 1
    assert isinstance(type(ast.statements[0].else_body[0]), type(ProcedureCallStatement))