import pytest

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
        #Test declaration type
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
            taast = build_taast("int x; int x;")
        except Exception as e:
            assert isinstance(e, DuplicateDeclarationError), "ScopeError -x-> duplicate declaration"
        
        try:
            taast = build_taast("int x; sprite x;")
        except Exception as e:
            assert isinstance(e, DuplicateDeclarationError), "ScopeError -x-> duplicate declaration"      


class TestTypeAssignments:
    def test_assignment_type(self):
        # Test assignment type
        
        taast = build_taast("int x; x = 2;")
        assert isinstance(taast.statements[1].target.var_type, IntType), "ass target -> int"
        assert isinstance(taast.statements[1].value.var_type, IntType), "ass value -> int"
        
        taast = build_taast("""sprite x; x = "binarys";""")
        assert isinstance(taast.statements[1].target.var_type, SpriteType), "ass target -> sprite"
        assert isinstance(taast.statements[1].value.var_type, StringType), "ass value -> string"
        
        taast = build_taast("""tilemap x; x = "binarys";""")
        assert isinstance(taast.statements[1].target.var_type, TileMapType), "ass target -> tilemap"
        assert isinstance(taast.statements[1].value.var_type, StringType), "ass value -> string"
        
        taast = build_taast("""tileset x; x = "binarys";""")
        assert isinstance(taast.statements[1].target.var_type, TilemapType), "ass target -> tileset"
        assert isinstance(taast.statements[1].value.var_type, StringType), "ass value -> string"
        
        try:
            taast = build_taast("sprite x; x = 1;")
        except Exception as e:
            assert isinstance(e, InvalidTypeError), "sprite var -x-> string"
            
            
    def test_assignment_scope_undeclared(self):
        # Test assignment scope
        try:
            taast = build_taast("x = 2;")
        except Exception as e:
            assert isinstance(e, UndeclaredVariableError), "ScopeError -x-> undeclared"
        
        try:
            taast = build_taast("int x = 1; if (x > 0) { y = 2; }")
        except Exception as e:
            assert isinstance(e, UndeclaredVariableError), "ScopeError -x-> undeclared"


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
            taast = build_taast("int x = 32; int x = 2;")
        except Exception as e:
            assert isinstance(e, DuplicateDeclarationError), "ScopeError -x-> duplicate declaration"
        
        try:
            taast = build_taast("int x = 32; sprite x = 2;")
        except Exception as e:
            assert isinstance(e, DuplicateDeclarationError), "ScopeError -x-> duplicate declaration"
            
        try:       
            taast = build_taast("int y = 1; if (1) { int y = 2; }")
        except Exception as e:
            assert isinstance(e, DuplicateDeclarationError), "ScopeError -y-> duplicate declaration"


    def test_list_initialization_type(self):
        # Test list initialization
        taast = build_taast("list x = [1, 2, 3];")
        assert isinstance(taast.statements[0].var_type, ListType), "list init -> list"
        assert isinstance(taast.statements[0].values[0].var_type, IntType), "list init value -> int"
        assert isinstance(taast.statements[0].values[2].var_type, IntType), "list init value -> int"
        

    def test_list_initialization_scope(self):
        # Test list initialization scope
        try:
            taast = build_taast("list x = [1, 2, 3]; list x = [4, 5, 6];")
        except Exception as e:
            assert isinstance(e, DuplicateDeclarationError), "ScopeError -x-> duplicate declaration"
        
        try:
            taast = build_taast("list x = [1, 2, 3]; sprite x = [4, 5, 6];")
        except Exception as e:
            assert isinstance(e, TypeMismatchError), "ScopeError -x-> duplicate declaration"
            
            
            
