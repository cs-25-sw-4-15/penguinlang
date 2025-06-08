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
from src.LiteralMerger import *


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
    merger = LiteralMerger()
    merger.merge_Program(tree)

    
    return tree



class TestLiteralMerging:
    def testSimpleLiteral(self):
        code = """
        int x = (5+5+5+5+5+5+5+5+5);
        """
        merged_tree = build_taast(code)

        assert(isinstance(merged_tree.statements[0].value, IntegerLiteral))
        assert(merged_tree.statements[0].value.value == "45")

    def testSimpleMultiplication(self):
        code = """
        int x = (3*4*2);
        """
        merged_tree = build_taast(code)
        assert(isinstance(merged_tree.statements[0].value, IntegerLiteral))
        assert(merged_tree.statements[0].value.value == "24")

    def testSimpleSubtraction(self):
        code = """
        int x = (100-25-10);
        """
        merged_tree = build_taast(code)
        assert(isinstance(merged_tree.statements[0].value, IntegerLiteral))
        assert(merged_tree.statements[0].value.value == "65")

    def testMixedArithmetic(self):
        code = """
        int x = (10*5-25+15);
        """
        merged_tree = build_taast(code)
        assert(isinstance(merged_tree.statements[0].value, IntegerLiteral))
        assert(merged_tree.statements[0].value.value == "40")

    def testEightBitBoundary(self):
        code = """
        int x = (255);
        """
        merged_tree = build_taast(code)
        assert(isinstance(merged_tree.statements[0].value, IntegerLiteral))
        assert(merged_tree.statements[0].value.value == "255")

    def testEightBitBoundary(self):
        code = """
        int x = (255 + 10);
        """
        merged_tree = build_taast(code)
        assert(isinstance(merged_tree.statements[0].value, IntegerLiteral))
        assert(merged_tree.statements[0].value.value == "9")