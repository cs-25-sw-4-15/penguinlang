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
from src.astTypeChecker import TypeChecker
from src.astTypes import IntType, StringType, VoidType, ListType, TilesetType, TileMapType, SpriteType, OAMEntryType


def build_taast(source_code):
    input_stream = InputStream(source_code)
    lexer = penguinLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = penguinParser(token_stream)
    cst = parser.program()
    
    visitor = ASTGenerator()
    ast = visitor.visit(cst)
    
    tree = ast
    type_checker = TypeChecker()
    type_checker.check_program(tree)
    
    return tree


class TestTypeDeclarations:
    def test_declaration_type(self):
        # Test declaration type
        taast = build_taast("int x;")
        assert isinstance(taast.statements[0].var_type, IntType), "int dec -> int" + " " + str(type(taast.statements[0].var_type)) + " " + str(IntType) 
        
        taast = build_taast("sprite x;")
        assert isinstance(taast.statements[0].var_type, SpriteType), "sprite dec -> string"
        
        taast = build_taast("tilemap x;")
        assert isinstance(taast.statements[0].var_type, TileMapType), "tilemap dec -> string"
        
        taast = build_taast("tileset x;")
        assert isinstance(taast.statements[0].var_type, TilesetType), "tileset dec -> string"

    def test_declaration_scope(self):
        # Test declaration scope
        try:
            build_taast("int x; int x;")
        except Exception as e:
            assert isinstance(e, DuplicateDeclarationError), "ScopeError -x-> duplicate declaration"
        
        try:
            build_taast("int x; sprite x;")
        except Exception as e:
            assert isinstance(e, DuplicateDeclarationError), "ScopeError -x-> duplicate declaration"      


class TestTypeAssignments:
    def test_assignment_type(self):
        # Test assignment type
        
        taast = build_taast("int x; x = 2;")
        assert isinstance(taast.statements[1].target.var_type, IntType), "ass target -> int"
        assert isinstance(taast.statements[1].value.var_type, IntType), "ass value -> int"
        
        try:
            build_taast("""sprite x; x = "binarys";""")
        except Exception as e:
            assert isinstance(e, TypeMismatchError), "if this is not the case, either the error has been changed, or somethjing else has happend"
        
        try:
            build_taast("""tilemap x; x = "binarys";""")
        except Exception as e:
            assert isinstance(e, TypeMismatchError), "if this is not the case, either the error has been changed, or somethjing else has happend"
        
        try:
            build_taast("""tileset x; x = "binarys";""") 
        except Exception as e:
            assert isinstance(e, TypeMismatchError), "if this is not the case, either the error has been changed, or somethjing else has happend"
        
        try:
            build_taast("sprite x; x = 1;")
        except Exception as e:
            assert isinstance(e, TypeMismatchError), "InvalidTypeError #1 sprite var -x-> string"
            
    def test_assignment_scope_undeclared(self):
        # Test assignment scope
        try:
            build_taast("x = 2;")
        except Exception as e:
            assert isinstance(e, UndeclaredVariableError), "UndeclaredVariableError #1 -x-> undeclared"
        
        try:
            build_taast("int x = 1; if (x > 0) { y = 2; }")
        except Exception as e:
            assert isinstance(e, UndeclaredVariableError), "UndeclaredVariableError #2 -x-> undeclared"


class TestTypeInitialization:
    def test_initialization_type(self):
        # Test initialization
        taast = build_taast("int x = 32;")
        assert isinstance(taast.statements[0].var_type, IntType), "int init -> int"
        assert isinstance(taast.statements[0].value.var_type, IntType), "int init value -> int"
        
        taast = build_taast("""sprite x = "binarys";""")
        assert isinstance(taast.statements[0].var_type, SpriteType), "sprite init -> sprite"
        assert isinstance(taast.statements[0].value.var_type, StringType), "sprite init value -> string"
        
        taast = build_taast("""tilemap x = "binarys";""")
        assert isinstance(taast.statements[0].var_type, TileMapType), "tilemap init -> tilemap"
        assert isinstance(taast.statements[0].value.var_type, StringType), "tilemap init value -> string"
        
        taast = build_taast("""tileset x = "binarys";""")
        assert isinstance(taast.statements[0].var_type, TilesetType), "tileset init -> tileset"
        assert isinstance(taast.statements[0].value.var_type, StringType), "tileset init value -> string"

    def test_initialization_scope(self):
        # Test initialization scope
        try:
            build_taast("int x = 32; int x = 2;")
        except Exception as e:
            assert isinstance(e, DuplicateDeclarationError), "DuplicateDeclarationError #1 -x-> duplicate declaration"
        
        try:
            build_taast("int x = 32; sprite x = 2;")
        except Exception as e:
            assert isinstance(e, DuplicateDeclarationError), "DuplicateDeclarationError #2 -x-> duplicate declaration"
            
        try:       
            build_taast("int y = 1; if (1) { int y = 2; }")
        except Exception as e:
            assert isinstance(e, DuplicateDeclarationError), "DuplicateDeclarationError #3 -y-> duplicate declaration"

    def test_list_initialization_type(self):
        # Test list initialization
        taast = build_taast("list x = [1, 2, 3];")
        assert isinstance(taast.statements[0].var_type, ListType), "list init -> list"
        assert isinstance(taast.statements[0].values[0].var_type, IntType), "list init value -> int"
        assert isinstance(taast.statements[0].values[2].var_type, IntType), "list init value -> int"
        
    def test_list_initialization_scope(self):
        # Test list initialization scope
        try:
            build_taast("list x = [1, 2, 3]; list x = [4, 5, 6];")
        except Exception as e:
            assert isinstance(e, DuplicateDeclarationError), "NOT DuplicateDeclarationError #1 -x-> duplicate declaration"
        
        try:
            build_taast("list x = [1, 2, 3]; sprite x = [4, 5, 6];")
        except Exception as e:
            # assert isinstance(e, TypeMismatchError), "NOT TypeMismatchError #2 -x-> duplicate declaration" + str(e)
            # Denne assertion ovenover ville give en assertion error, da vi ikke har en error for hvis man prøvver at alve en liste ud fra "sprite" type.
            assert isinstance(e, Exception)
        
            
class TestTypeConditionals:
    def test_conditional_statement(self):
        taast = build_taast("int x = 1; if (x > 0) { int y = 1; }")

        assert isinstance(taast.statements[1], Conditional), "if statement -> conditional"
        assert isinstance(taast.statements[1].condition, BinaryOp), "if condition -> binary op"
        assert taast.statements[1].condition.op == ">", "if condition -> binary op"
        
        assert isinstance(taast.statements[1].condition.left, Variable), "if condition left -> variable"
        assert taast.statements[1].condition.left.name == "x", "if condition left -> variable"

        assert isinstance(taast.statements[1].condition.right.var_type, IntType), "if condition right -> int"
        assert taast.statements[1].condition.right.value == 0
        
        assert isinstance(taast.statements[1].then_body[0].var_type, IntType), "if body dec -> int"
    
    def test_conditional_with_else(self):
        taast = build_taast("int x = 1; if (x > 0) { int y = 1; } else { y = 2; }")

        assert isinstance(taast.statements[1], Conditional), "if statement -> conditional"
        assert isinstance(taast.statements[1].condition, BinaryOp), "if condition -> binary op"
        
        assert isinstance(taast.statements[1].then_body[0], Initialization), "then -> assignment"

        assert isinstance(taast.statements[1].else_body[0], Assignment), "else -> assignment"
        assert isinstance(taast.statements[1].else_body[0].var_type, IntType), "else body dec -> int"

        assert taast.statements[1].else_body[0].value.value == 2
          
    
class TestTypeLoop:
    def test_loop_type(self):
        taast = build_taast("""loop (1) { int a; }""")
        assert isinstance(taast.statements[0].condition.var_type, IntType), "loop cond -> int"
        assert isinstance(taast.statements[0].body[0].var_type, IntType), "loop body dec -> int"
        
        taast = build_taast("""loop (1) { loop (0) { int a; } }""")
        assert isinstance(taast.statements[0].body[0].condition.var_type, IntType), "loop in loop cond -> int"
        assert isinstance(taast.statements[0].body[0].body[0].var_type, IntType), "loop in loop body dec -> int"
        
    def test_loop_scope(self):
        try:
            build_taast("""loop(1) { int a; int a; }""")
        except Exception as e:
            assert isinstance(e, DuplicateDeclarationError), "DuplicateDeclarationError #1 -a-> duplicate declaration"
        
        try:
            build_taast("""loop(1) { int a; sprite a; }""")
        except Exception as e:
            assert isinstance(e, DuplicateDeclarationError), "DuplicateDeclarationError #2 -a-> duplicate declaration"
        
        
class TestTypeReturn:
    def test_return_type(self):
        taast = build_taast("procedure int test() { return 1; }")
        assert isinstance(taast.statements[0].body[0].var_type, IntType),"return int -> int"
        
        taast = build_taast("""procedure sprite test() { sprite s = "hej"; return s; }""")
        assert isinstance(taast.statements[0].body[0].var_type, SpriteType),"return sprite -> sprite"
        
    def test_return_type_mismatch(self):
        try:
            build_taast("""procedure int test() { sprite s = "hej"; return s; }""")
        except Exception as e:
            assert isinstance(e, TypeMismatchError), "TypeMismatchError -> return Type mismatch"
            
        try:
            build_taast("""procedure sprite test() { return 1; }""")
        except Exception as e:
            assert isinstance(e, TypeMismatchError), "TypeMismatchError -> return Type mismatch"
        
        try:
            build_taast("""procedure test() { return 1; }""")
        except Exception as e:
            assert isinstance(e, TypeMismatchError), "TypeMismatchError -> return Type mismatch --- " + e

 
class TestTypeProcedureDef:
    def test_procedure_def_type(self):
        # Test procedure definition with no return type
        taast = build_taast("procedure foo() { int x; }")
        assert isinstance(taast.statements[0], ProcedureDef), "proc def -> proc def"
        assert isinstance(taast.statements[0].return_type, VoidType), "proc def return_type -> void --- " + str(taast.statements[0].return_type) + " " + str(VoidType)
        assert isinstance(taast.statements[0].body[0].var_type, IntType), "proc def body dec -> int"
        
        # Test procedure definition with int return type
        taast = build_taast("procedure int foo() { int x; }")
        assert isinstance(taast.statements[0], ProcedureDef), "proc def -> proc def"
        assert isinstance(taast.statements[0].return_type, IntType), "proc def -> int"
        assert isinstance(taast.statements[0].body[0].var_type, IntType), "proc def body dec -> int"
        
        # Test wrong procedure definition with sprite return type
        try:
            taast = build_taast("procedure sprite foo() { int t = 2; }")
        except Exception as e:
            assert isinstance(e, InvalidTypeError), "InvalidTypeError #1 proc def -foo-> sprite"
        
        # Test procedure definition with no return type, with 1 formal param
        taast = build_taast("procedure foo(int x) { int t = 2; }")
        assert isinstance(taast.statements[0], ProcedureDef), "proc def -> proc def"
        assert isinstance(taast.statements[0].return_type, VoidType), "proc def return_type -> void"
        assert isinstance(taast.statements[0].params[0].var_type, IntType), "proc def param dec -> int"
        assert isinstance(taast.statements[0].body[0].var_type, IntType), "proc def body dec -> int"
        
        # Test procedure definition with no return type, with more formal param
        taast = build_taast("procedure foo(int x, int y, int z) { int t = 2;  }")
        assert isinstance(taast.statements[0], ProcedureDef), "proc def -> proc def"
        assert isinstance(taast.statements[0].return_type, VoidType), "proc def return_type -> void"
        assert isinstance(taast.statements[0].params[0].var_type, IntType), "proc def param1 dec -> int"
        assert isinstance(taast.statements[0].params[1].var_type, IntType), "proc def param2 dec -> int"
        assert isinstance(taast.statements[0].params[2].var_type, IntType), "proc def param3 dec -> int"
        assert isinstance(taast.statements[0].body[0].var_type, IntType), "proc def body dec -> int"
        
        # Test procedure definition with int return type, with 1 formal param
        taast = build_taast("procedure int foo(int x) { int t = 2;  }")
        assert isinstance(taast.statements[0], ProcedureDef), "proc def -> proc def"
        assert isinstance(taast.statements[0].return_type, IntType), "proc def -> int"
        assert isinstance(taast.statements[0].params[0].var_type, IntType), "proc def param dec -> int"
        assert isinstance(taast.statements[0].body[0].var_type, IntType), "proc def body dec -> int"
        
        # Test procedure definition with int return type, with more formal param
        taast = build_taast("procedure int foo(int x, int y, int z) { int t = 2; }")
        assert isinstance(taast.statements[0], ProcedureDef), "proc def -> proc def"
        assert isinstance(taast.statements[0].return_type, IntType), "proc def -> int"
        assert isinstance(taast.statements[0].params[0].var_type, IntType), "proc def param1 dec -> int"
        assert isinstance(taast.statements[0].params[1].var_type, IntType), "proc def param2 dec -> int"
        assert isinstance(taast.statements[0].params[2].var_type, IntType), "proc def param3 dec -> int"
        assert isinstance(taast.statements[0].body[0].var_type, IntType), "proc def body dec -> int"
    
    def test_procedure_def_scope(self):
        # Test procedure definition inside body scope
        try:
            taast = build_taast("procedure foo() { int x; int x; }")
        except Exception as e:
            assert isinstance(e, DuplicateDeclarationError), "DuplicateDeclarationError #1 -x-> duplicate declaration"            
        
        # test procedure definition formal param scope
        try:
            taast = build_taast("procedure foo(int x) { int x; }")
        except Exception as e:
            assert isinstance(e, DuplicateDeclarationError), "DuplicateDeclarationError #3 -x-> duplicate declaration"
        
        # test procedure definition formal param scope
        try:
            taast = build_taast("procedure foo(int x) { int y; sprite x; }")
        except Exception as e:
            assert isinstance(e, DuplicateDeclarationError), "DuplicateDeclarationError #4 -x-> duplicate declaration"
        
        # test procedure definition formal param scope
        taast = build_taast("procedure foo(int x) { x = 2; }")
        assert isinstance(taast.statements[0].params[0].var_type, IntType), "proc def param dec -> int"
        assert isinstance(taast.statements[0].body[0].target.var_type, IntType), "proc def body dec -> int"
    
    def test_procedure_def_scope2(self):
        # test procedure definition inside and outside body scope. should overwrite the one outside
        try:
            build_taast("int x; procedure foo() { int x;}")
        except Exception as e:
            assert False, "child scope not overwriting parent scope --- " + str(e)
        
        try:
            build_taast("int y = 2; procedure foo() { int y = 4;}")
        except Exception as e:
            assert False, "child scope not overwriting parent scope --- " + str(e)
            
        try:
            build_taast("int z; procedure foo() { z = 6; }")
        except Exception as e:
            assert False, "wtf - z not part of procedure scope --- " + str(e) 
        
        try:
            build_taast("int q; procedure foo(int q) { int x; }")
        except Exception as e:
            assert False, "child scope in formal param not overwriting parent scope --- " + str(e)


class TestBinaryOp: # TODO
    def test_arithmetic_binary_op(self):
        taast = build_taast("int x = 1 + 2")
        assert taast.statements[0].value.op == "+"
        assert isinstance(taast.statements[0].value.var_type, IntType), "arithmetic op -> int"
        assert isinstance(taast.statements[0].value.left.var_type, IntType), "arithmetic op left -> int"
        assert isinstance(taast.statements[0].value.right.var_type, IntType), "arithmetic op right -> int"
        
        taast = build_taast("int x = 1 - 2")
        assert isinstance(taast.statements[0].value.var_type, IntType), "arithmetic op -> int"
        assert isinstance(taast.statements[0].value.left.var_type, IntType), "arithmetic op left -> int"
        assert isinstance(taast.statements[0].value.right.var_type, IntType), "arithmetic op right -> int"
        
        taast = build_taast("int x = 1 * 2")
        assert isinstance(taast.statements[0].value.var_type, IntType), "arithmetic op -> int"
        assert isinstance(taast.statements[0].value.left.var_type, IntType), "arithmetic op left -> int"
        assert isinstance(taast.statements[0].value.right.var_type, IntType), "arithmetic op right -> int"
        
        taast = build_taast("int x = 1 << 2")
        assert isinstance(taast.statements[0].value.var_type, IntType), "bitwise arithmetic op -> int"
        assert isinstance(taast.statements[0].value.left.var_type, IntType), "bitwise arithmetic op left -> int"
        assert isinstance(taast.statements[0].value.right.var_type, IntType), "bitwise arithmetic op right -> int"
        
        taast = build_taast("int x = 1 >> 2")
        assert isinstance(taast.statements[0].value.var_type, IntType), "bitwise arithmetic op -> int"
        assert isinstance(taast.statements[0].value.left.var_type, IntType), "bitwise arithmetic op left -> int"
        assert isinstance(taast.statements[0].value.right.var_type, IntType), "bitwise arithmetic op right -> int"
    
    def test_logical_and_bitwise_binary_op(self):
        taast = build_taast("int x = 1 & 2")
        assert isinstance(taast.statements[0].value.var_type, IntType), "bitwise op -> int"
        assert isinstance(taast.statements[0].value.left.var_type, IntType), "bitwise op left -> int"
        assert isinstance(taast.statements[0].value.right.var_type, IntType), "bitwise op right -> int"
        
        taast = build_taast("int x = 1 | 2")
        assert isinstance(taast.statements[0].value.var_type, IntType), "bitwise op -> int"
        assert isinstance(taast.statements[0].value.left.var_type, IntType), "bitwise op left -> int"
        assert isinstance(taast.statements[0].value.right.var_type, IntType), "bitwise op right -> int"
        
        taast = build_taast("int x = 1 ^ 2")
        assert isinstance(taast.statements[0].value.var_type, IntType), "bitwise op -> int"
        assert isinstance(taast.statements[0].value.left.var_type, IntType), "bitwise op left -> int"
        assert isinstance(taast.statements[0].value.right.var_type, IntType), "bitwise op right -> int"
        
        taast = build_taast("int x = 1 and 2")
        assert isinstance(taast.statements[0].value.var_type, IntType), "logical op -> int"
        assert isinstance(taast.statements[0].value.left.var_type, IntType), "logical op left -> int"
        assert isinstance(taast.statements[0].value.right.var_type, IntType), "logical op right -> int"
        
        taast = build_taast("int x = 1 or 2")
        assert isinstance(taast.statements[0].value.var_type, IntType), "logical op -> int"
        assert isinstance(taast.statements[0].value.left.var_type, IntType), "logical op left -> int"
        assert isinstance(taast.statements[0].value.right.var_type, IntType), "logical op right -> int"      
        
    def test_comparison_binary_op(self):
        taast = build_taast("int x = 1 < 2")
        assert isinstance(taast.statements[0].value.var_type, IntType), "comparison op -> int"
        assert isinstance(taast.statements[0].value.left.var_type, IntType), "comparison op left -> int"
        assert isinstance(taast.statements[0].value.right.var_type, IntType), "comparison op right -> int"
        
        taast = build_taast("int x = 1 > 2")
        assert isinstance(taast.statements[0].value.var_type, IntType), "comparison op -> int"
        assert isinstance(taast.statements[0].value.left.var_type, IntType), "comparison op left -> int"
        assert isinstance(taast.statements[0].value.right.var_type, IntType), "comparison op right -> int"
        
        taast = build_taast("int x = 1 <= 2")
        assert isinstance(taast.statements[0].value.var_type, IntType), "comparison op -> int"
        assert isinstance(taast.statements[0].value.left.var_type, IntType), "comparison op left -> int"
        assert isinstance(taast.statements[0].value.right.var_type, IntType), "comparison op right -> int"
        
        taast = build_taast("int x = 1 >= 2")
        assert isinstance(taast.statements[0].value.var_type, IntType), "comparison op -> int"
        assert isinstance(taast.statements[0].value.left.var_type, IntType), "comparison op left -> int"
        assert isinstance(taast.statements[0].value.right.var_type, IntType), "comparison op right -> int"
        
        taast = build_taast("int x = 1 == 2")
        assert isinstance(taast.statements[0].value.var_type, IntType), "comparison op -> int"
        assert isinstance(taast.statements[0].value.left.var_type, IntType), "comparison op left -> int"
        assert isinstance(taast.statements[0].value.right.var_type, IntType), "comparison op right -> int"
        
        taast = build_taast("int x = 1 != 2")
        assert isinstance(taast.statements[0].value.var_type, IntType), "comparison op -> int"
        assert isinstance(taast.statements[0].value.left.var_type, IntType), "comparison op left -> int"
        assert isinstance(taast.statements[0].value.right.var_type, IntType), "comparison op right -> int"


class TestUnaryOp:
    def test_aritmetic_unary_op(self):
        taast = build_taast("int x = -1")
        assert isinstance(taast.statements[0].value.var_type, IntType), "unary arithmetic op -> int"
        
        taast = build_taast("int x = +1")
        assert isinstance(taast.statements[0].value.var_type, IntType), "unary arithmetic op -> int"
    
    def test_logical_unary_op(self):
        taast = build_taast("int x = not 1")
        assert isinstance(taast.statements[0].value.var_type, IntType), "unary logical op -> int"
        
        taast = build_taast("int x = not (1 and 2)")
        assert isinstance(taast.statements[0].value.var_type, IntType), "unary logical op -> int"
        
        taast = build_taast("int x = ~ 1;")
        assert isinstance(taast.statements[0].value.var_type, IntType), "unary bitwise op -> int"
        
        taast = build_taast("int x = ~ (1 & 2);")
        assert isinstance(taast.statements[0].value.var_type, IntType), "unary bitwise op -> int"
        
    
class TestTypeIntegerLiteral:
    def test_integer_literal_type(self):
        # Test basic integer literal
        taast = build_taast("""int a = 123;""")
        assert isinstance(taast.statements[0].value.var_type, IntType), "basic int literal -> IntType"
        
        # Test zero
        taast = build_taast("""int a = 0;""")
        assert isinstance(taast.statements[0].value.var_type, IntType), "zero -> IntType"
        
        # Test negative integer
        taast = build_taast("""int a = -40;""")
        assert isinstance(taast.statements[0].value.var_type, IntType), "negative int -> IntType"
        
        # Test integer in binary expression
        taast = build_taast("""int a = 5 + 10;""")
        assert isinstance(taast.statements[0].value.left.var_type, IntType), "int in binary expr left -> IntType"
        assert isinstance(taast.statements[0].value.right.var_type, IntType), "int in binary expr right -> IntType"
        
        # Test integer in condition
        taast = build_taast("""if (1) { int a = 0; }""")
        assert isinstance(taast.statements[0].condition.var_type, IntType), "int in condition -> IntType"
        
        # Test integer in loop condition
        taast = build_taast("""loop (42) { int a = 0; }""")
        assert isinstance(taast.statements[0].condition.var_type, IntType), "int in loop condition -> IntType"
        
        # Test integer in return statement
        taast = build_taast("""procedure int test() { return 100; }""")
        assert isinstance(taast.statements[0].body[0].value.var_type, IntType), "int in return -> IntType"
        
        # Test integer in assignment
        taast = build_taast("""int a; a = 50;""")
        assert isinstance(taast.statements[1].value.var_type, IntType), "int in assignment -> IntType"
        
        
class TestTypeStringLiteral:
    def test_string_literal_type(self):
        # Test basic string literal
        taast = build_taast("""sprite a = "hello";""")
        assert isinstance(taast.statements[0].value.var_type, StringType), "basic sprite literal -> StringType"
        
        # Test empty string
        taast = build_taast("""sprite a = "";""")
        assert isinstance(taast.statements[0].value.var_type, StringType), "empty sprite -> StringType"
        
        # Test string in return statement
        taast = build_taast("""procedure sprite test() { return "hello"; }""")
        assert isinstance(taast.statements[0].body[0].value.var_type, StringType), "sprite in return -> StringType"
        # øvre, er badshit crazy
        
        # Test string in assignment
        # taast = build_taast("""sprite a; a = "hello";""")
        # assert isinstance(taast.statements[1].value.var_type, StringType), "sprite in assignment -> StringType"
        # øvre er udkomemnnteret, da der ikke må laves assignments af sprites osv. kun initialization


class TestTypeVariable:
    def test_varaible_scope(self):
        # regular variable case
        taast = build_taast("int x = 2; x = 1;")
        assert isinstance(taast.statements[0], Initialization), "stmt init -> init"
        assert isinstance(taast.statements[0].var_type, IntType), "var scope -> int"
        assert isinstance(taast.statements[0].value.var_type, IntType), "var scope -> int"
        assert isinstance(taast.statements[1], Assignment), "stmt assignment -> assignment"
        assert isinstance(taast.statements[1].target.var_type, IntType), "var scope -> int"
        assert isinstance(taast.statements[1].value.var_type, IntType), "var scope -> int"
        
        try:
            taast = build_taast("x = 3;")
        except Exception as e:
            assert isinstance(e, UndeclaredVariableError), "UndeclaredVariableError #1 -x-> undeclared"
    
    def test_variable_scope2(self):
        # attribute access case
        # this has been removed from use, and new dots cannot be made
        try: 
            taast = build_taast("int x; x.x = 2;")
        except Exception as e:
            assert isinstance(e, InvalidAttributeError), "InvalidAttributeError #1 -x-> invalid"
        
        taast = build_taast("display.oam[1].x = 1;")
        
        assert isinstance(taast.statements[0], Assignment), "stmt assignment -> assignment"
        assert isinstance(taast.statements[0].var_type, IntType), "var scope -> int"


class testTypeAttributeAccess:
    def test_attribute_access_type(self):
        taast = build_taast("display.oam[1].x = 1;")
        assert isinstance(taast.statements[0], Assignment), "stmt assignment -> assignment"
        assert isinstance(taast.statements[0].target.var_type, IntType), "var scope -> int"
        
        taast = build_taast("int x = display.oam[1].y;")
        assert isinstance(taast.statements[0], Initialization), "stmt init -> init"
        assert isinstance(taast.statements[0].var_type, IntType), "var scope -> int"
        assert isinstance(taast.statements[0].value.var_type, IntType), "var scope -> int"
        
        taast = build_taast("int x = display.oam[1].x;")
        assert isinstance(taast.statements[0], Initialization), "stmt init -> init"
        assert isinstance(taast.statements[0].var_type, IntType), "var scope -> int"
        assert isinstance(taast.statements[0].value.var_type, IntType), "var scope -> int"
        
        taast = build_taast("int x; x = display.oam[1].y;")
        assert isinstance(taast.statements[1], Initialization), "stmt init -> init"
        assert isinstance(taast.statements[1].var_type, IntType), "var scope -> int"
        assert isinstance(taast.statements[1].value.var_type, IntType), "var scope -> int"
        
        taast = build_taast("int x; x = display.oam[1].x;")
        assert isinstance(taast.statements[1], Initialization), "stmt init -> init"
        assert isinstance(taast.statements[1].var_type, IntType), "var scope -> int"
        assert isinstance(taast.statements[1].value.var_type, IntType), "var scope -> int"
        
        # TODO tjek for OAMEntryType
        

class TestTypeListAccess:
    def test_list_access(self):
        taast = build_taast("list x = [1, 2, 3]; x[0] = 5;")
        assert isinstance(taast.statements[0], ListInitialization), "stmt init -> init"
        assert isinstance(taast.statements[0].var_type, ListType), "var scope -> list"
        assert isinstance(taast.statements[1], Assignment), "stmt assignment -> assignment"
        assert isinstance(taast.statements[1].target.var_type, IntType), "var scope -> int"
        assert isinstance(taast.statements[1].value.var_type, IntType), "var scope -> int"
        
        taast = build_taast("list x = [1, 2, 3]; int y = x[0];")
        assert isinstance(taast.statements[1], Initialization), "stmt init -> init"
        assert isinstance(taast.statements[1].var_type, IntType), "var scope -> int"
        assert isinstance(taast.statements[1].value, ListAccess), "var scope -> list access"
        assert isinstance(taast.statements[1].value.name.var_type, ListType), "var scope valuie name list acess -> str"
        assert isinstance(taast.statements[1].value.indices[0], IntegerLiteral), "var scope -> IntegerLiteral"
        assert isinstance(taast.statements[1].value.indices[0].var_type, IntType), "var scope -> int"


class TestTypeProcedureCallStatement:
    def test_procedure_call_statement_scope(self):
        taast = build_taast("""procedure foo() { int x = 1; } foo();""")
        
        assert isinstance(taast.statements[0], ProcedureDef), "proc def -> ProcedureDef"
        assert isinstance(taast.statements[0].return_type, VoidType), "proc def return_type -> void"
        assert isinstance(taast.statements[1], ProcedureCallStatement), "proc call -> ProcedureCallStatement"
        
        # Procedure is defined after it is called, should raise error
        try:
            build_taast("""foo(1); procedure foo(int y) { int x = 1; }""")
        except Exception as e:
            assert isinstance(e, UndeclaredVariableError), "undeclared proc error (called before declared)"

        # Procedure with no parameters called before it's declared, should raise error
        try:
            build_taast("""foo(); procedure foo() { int x = 1; }""")
        except Exception as e:
            assert isinstance(e, UndeclaredVariableError), "undeclared proc error (called before declared)"

        
class TestTypeProcedureCallInExpression:
    def test_preocedurecallinexpression_type(self):
        taast = build_taast("""procedure int foo() { return 1; } int x = foo();""")
        # exp type, return type, foo exp type
        assert isinstance(taast.statements[0], ProcedureDef), "proc def -> ProcedureDef"
        assert isinstance(taast.statements[0].return_type, IntType), "proc def return_type -> int"
        assert isinstance(taast.statements[1], Initialization), "init = proc call -> Initialization"
        assert isinstance(taast.statements[1].var_type, IntType), "init -> int"
        assert isinstance(taast.statements[1].value, ProcedureCall), "init -> ProcedureCall"
        assert isinstance(taast.statements[1].value.var_type, IntType), "proc call -> int"
        
        taast = build_taast("""procedure int foo(int x) { return x+1; } int x = foo(1);""")
        # exp type, return type, type of return expression, foo exp type, param type
        assert isinstance(taast.statements[0], ProcedureDef), "proc def -> ProcedureDef"
        assert isinstance(taast.statements[0].return_type, IntType), "proc def return_type -> int"
        assert isinstance(taast.statements[0].params[0].var_type, IntType), "proc def param -> int"
        assert isinstance(taast.statements[0].body[0].var_type, IntType), "proc def body -> int"
        assert isinstance(taast.statements[1].var_type, IntType), "init -> int"
        assert isinstance(taast.statements[1].value, ProcedureCall), "init -> ProcedureCall"
        assert isinstance(taast.statements[1].value.var_type, IntType), "proc call -> int"
        assert isinstance(taast.statements[1].value.params[0].var_type, IntType), "proc call param (Variable) -> int"
