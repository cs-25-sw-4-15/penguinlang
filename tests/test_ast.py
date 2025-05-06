
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from antlr4 import InputStream, CommonTokenStream
from src.generated.penguinLexer import penguinLexer
from src.generated.penguinParser import penguinParser
from src.astClasses import *
from src.astGenerator import ASTGenerator
from src.customErrors import *




def build_ast(source_code):
    input_stream = InputStream(source_code)
    lexer = penguinLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = penguinParser(token_stream)
    parse_tree = parser.program()
    
    visitor = ASTGenerator()
    return visitor.visit(parse_tree)

class TestASTDeclarations:
    def test_declaration(self):
        ast = build_ast("int x;")
        assert isinstance(ast.statements[0], Declaration)
        assert len(ast.statements) == 1
        assert ast.statements[0].var_type == "int"
        assert ast.statements[0].name == "x"

    def test_multiple_declarations(self):
        ast = build_ast("int x; int y;")
        
        assert len(ast.statements) == 2
        assert isinstance(ast.statements[0], Declaration)
        assert isinstance(ast.statements[1], Declaration)
        assert ast.statements[0].var_type == "int"
        assert ast.statements[0].name == "x"
        assert ast.statements[1].var_type == "int"
        assert ast.statements[1].name == "y"


class TestASTAssignments:
    def test_simple_assignment(self):
        ast = build_ast("x = 42;")
        
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], Assignment)
        assert isinstance(ast.statements[0].target, Variable)
        assert ast.statements[0].target.name == "x"
        assert isinstance(ast.statements[0].value, IntegerLiteral)
        assert ast.statements[0].value.value == 42

    def test_list_assignment(self):
        ast = build_ast("x[0] = 42;")
        
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], Assignment)
        assert isinstance(ast.statements[0].target, ListAccess)
        assert isinstance(ast.statements[0].target.name, Variable)
        assert ast.statements[0].target.name.name == "x"
        assert isinstance(ast.statements[0].target.indices[0], IntegerLiteral)

        assert ast.statements[0].target.indices[0].value == 0
        assert isinstance(ast.statements[0].value, IntegerLiteral)
        assert ast.statements[0].value.value == 42


class TestASTInitializations:
    def test_simple_initialization(self):
        ast = build_ast("int x = 42;")
        
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], Initialization)
        assert ast.statements[0].var_type == "int"
        assert ast.statements[0].name == "x"
        assert isinstance(ast.statements[0].value, IntegerLiteral)
        assert ast.statements[0].value.value == 42

    def test_list_initialization(self):
        ast = build_ast("list x = [1, 2, 3];")
        
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], ListInitialization)
        assert ast.statements[0].name == "x"
        assert len(ast.statements[0].values) == 3
        assert all(isinstance(val, IntegerLiteral) for val in ast.statements[0].values)
        assert [val.value for val in ast.statements[0].values] == [1, 2, 3]


class TestASTExpressions:
    def test_binary_expression(self):
        ast = build_ast("x = a + b;")
        
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], Assignment)
        assert isinstance(ast.statements[0].value, BinaryOp)
        assert ast.statements[0].value.op == "+"
        assert isinstance(ast.statements[0].value.left, Variable)
        assert ast.statements[0].value.left.name == "a"
        assert isinstance(ast.statements[0].value.right, Variable)
        assert ast.statements[0].value.right.name == "b"

    def test_complex_binary_expression(self):
        ast = build_ast("x = a + b * c;")
        
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

    def test_parenthesized_expression(self):
        ast = build_ast("x = (a + b) * c;")
        
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], Assignment)
        assert isinstance(ast.statements[0].value, BinaryOp)
        assert ast.statements[0].value.op == "*"
        assert isinstance(ast.statements[0].value.left, BinaryOp)
        assert ast.statements[0].value.left.op == "+"
        assert isinstance(ast.statements[0].value.right, Variable)
        assert ast.statements[0].value.right.name == "c"
    

class TestASTLiterals:
    def test_integer_literal(self):
        ast = build_ast("x = 42;")
        
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], Assignment)
        assert isinstance(ast.statements[0].value, IntegerLiteral)
        assert ast.statements[0].value.value == 42

    def test_hex_literal(self):
        ast = build_ast("x = 0x2A;")
        
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], Assignment)
        assert isinstance(ast.statements[0].value, IntegerLiteral)
        assert ast.statements[0].value.value == 42  # 0x2A = 42

    def test_binary_literal(self):
        """Test binary literal AST construction."""
        ast = build_ast("x = 0b101010;")
        
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], Assignment)
        assert isinstance(ast.statements[0].value, IntegerLiteral)
        assert ast.statements[0].value.value == 42  # 0b101010 = 42


class TestASTConditionals:
    def test_conditional_statement(self):
        ast = build_ast("if (x > 0) { y = 1; }")
        
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

    def test_conditional_with_else(self):
        ast = build_ast("if (x > 0) { y = 1; } else { y = 2; }")
        
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], Conditional)
        assert isinstance(ast.statements[0].condition, BinaryOp)
        assert len(ast.statements[0].then_body) == 1
        assert isinstance(ast.statements[0].then_body[0], Assignment)
        assert len(ast.statements[0].else_body) == 1
        assert isinstance(ast.statements[0].else_body[0], Assignment)
        assert isinstance(ast.statements[0].else_body[0].value, IntegerLiteral)
        assert ast.statements[0].else_body[0].value.value == 2


class TestASTLoops:
    def test_loop_statement(self):
        ast = build_ast("loop (i < 10) { i = i + 1; }")
        
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


class TestASTProcedures:
    def test_procedure_call(self):
        ast = build_ast("print(42);")
        
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], ProcedureCallStatement)
        assert isinstance(ast.statements[0].call, ProcedureCall)
        assert isinstance(ast.statements[0].call.name, Variable)
        assert ast.statements[0].call.name.name == "print"
        assert len(ast.statements[0].call.params) == 1
        assert isinstance(ast.statements[0].call.params[0], IntegerLiteral)
        assert ast.statements[0].call.params[0].value == 42

    def test_procedure_call_multiple_args(self):
        ast = build_ast("print(42, x);")
        
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], ProcedureCallStatement)
        assert isinstance(ast.statements[0].call, ProcedureCall)
        assert len(ast.statements[0].call.params) == 2
        assert isinstance(ast.statements[0].call.params[0], IntegerLiteral)
        assert isinstance(ast.statements[0].call.params[1], Variable)

    def test_procedure_definition(self):
        ast = build_ast("procedure int add(int a, int b) { return a + b; }")
        
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], ProcedureDef)
        assert ast.statements[0].return_type == "int"
        assert ast.statements[0].name == "add"
        assert len(ast.statements[0].params) == 2
        assert ast.statements[0].params[0].name == "a"
        assert ast.statements[0].params[0].var_type == "int"
        assert ast.statements[0].params[1].name == "b"
        assert ast.statements[0].params[1].var_type == "int"
        assert len(ast.statements[0].body) == 1
        assert isinstance(ast.statements[0].body[0], Return)
        assert isinstance(ast.statements[0].body[0].value, BinaryOp)
        assert ast.statements[0].body[0].value.op == "+"

    def test_void_procedure_definition(self):
        ast = build_ast("procedure printHello() { print(5); };")
        
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], ProcedureDef)
        assert ast.statements[0].return_type == "void"
        assert ast.statements[0].name == "printHello"
        assert len(ast.statements[0].params) == 0
        assert len(ast.statements[0].body) == 1
        assert isinstance(ast.statements[0].body[0], ProcedureCallStatement)

    def test_return_statement(self):
        ast = build_ast("procedure int foo() { return 42; }")
        
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], ProcedureDef)
        assert len(ast.statements[0].body) == 1
        assert isinstance(ast.statements[0].body[0], Return)
        assert isinstance(ast.statements[0].body[0].value, IntegerLiteral)
        assert ast.statements[0].body[0].value.value == 42


class TestASTLists:
    def test_list_access(self):
        """Test list access AST construction."""
        ast = build_ast("x = arr[i];")
        
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], Assignment)
        assert isinstance(ast.statements[0].value, ListAccess)
        assert isinstance(ast.statements[0].value.name, Variable)
        assert isinstance(ast.statements[0].value.indices[0], Variable)
        assert ast.statements[0].value.name.name == "arr"
        assert ast.statements[0].value.indices[0].name == "i"

    def test_nested_list_access(self):
        """Test nested list access AST construction."""
        ast = build_ast("x = arr[i][j];")
        
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], Assignment)
        assert isinstance(ast.statements[0].value, ListAccess)
        assert isinstance(ast.statements[0].value.name, Variable)
        assert ast.statements[0].value.name.name == "arr"
        assert isinstance(ast.statements[0].value.indices[0], Variable)
        assert isinstance(ast.statements[0].value.indices[1], Variable)
        assert ast.statements[0].value.indices[0].name == "i"
        assert ast.statements[0].value.indices[1].name == "j"


class TestASTattributes:
    def test_attribute_access(self):
        """Test attribute access AST construction."""
        ast = build_ast("x = obj.attr;")
        
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], Assignment)
        assert isinstance(ast.statements[0].value, AttributeAccess)
        assert isinstance(ast.statements[0].value.name, Variable)
        assert ast.statements[0].value.name.name == "obj"
        assert ast.statements[0].value.attribute == "attr"

    def test_chained_attribute_access(self):
        """Test chained attribute access AST construction."""
        ast = build_ast("x = obj.attr1.attr2;")
        
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], Assignment)
        assert isinstance(ast.statements[0].value, AttributeAccess)
        assert isinstance(ast.statements[0].value.name, AttributeAccess)
        assert isinstance(ast.statements[0].value.name.name, Variable)
        assert ast.statements[0].value.name.name.name == "obj"
        assert ast.statements[0].value.name.attribute == "attr1"
        assert ast.statements[0].value.attribute == "attr2"


class TestASTComplexStructures:
    def test_complex_nested_structure(self):
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
        assert isinstance(ast.statements[0], Conditional)
        assert isinstance(ast.statements[0].condition, BinaryOp)
        assert len(ast.statements[0].then_body) == 1
        assert isinstance(ast.statements[0].then_body[0], Loop)
        assert len(ast.statements[0].then_body[0].body) == 2
        assert isinstance(ast.statements[0].then_body[0].body[1], Conditional)
        assert len(ast.statements[0].else_body) == 1
        assert isinstance(ast.statements[0].else_body[0], ProcedureCallStatement)
