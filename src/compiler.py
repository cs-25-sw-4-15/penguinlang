"""Penguin Compiler

Containes the main logic for the compiler.
"""


# antlr4 modules
from antlr4 import FileStream, CommonTokenStream


# antl4 generated modules
from generated.penguinLexer import penguinLexer
from generated.penguinParser import penguinParser


# custom modules
from ast_classes import ASTNode
from ast_generator import ASTGenerator
from asttype_checker import TypeChecker


# other modules
import json
import pprint

class ASTEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ASTNode):
            # Convert ASTNode objects to dictionaries
            result = {}
            # Add class name for reconstruction
            result["__class__"] = obj.__class__.__name__
            # Add all attributes
            for key, value in obj.__dict__.items():
                result[key] = value
            return result
        # Special case for Type objects including VoidType, IntType, etc.
        elif obj.__class__.__name__ in ['VoidType', 'IntType', 'StringType', 'TilesetType', 
                                       'TileMapType', 'SpriteType', 'OAMEntryType', 'ListType']:
            return {"__class__": obj.__class__.__name__}
        # Let the base class handle other types
        return super().default(obj)


def read_input_file(input_file: str):
    """Reads the input file and returns a FileStream.
    
    Args:
        input_file (str): The path to the input file.
    """
    
    print("Reading file...")
    
    return FileStream(input_file, encoding="utf-8")


def concrete_syntax_tree(input_stream: str, p: bool = False):
    """Creates a concrete syntax tree (CST) from the input stream.
    
    Lexing -> tokenstresm -> parsing -> parse tree (CST)
    
    Args:
        input_stream (str): The input stream to parse.
        
    Returns:
        tree (str): The parse tree (CST).
    """
    
    print("Lexing file...")
    lexer = penguinLexer(input_stream)
    
    print("Creating token stream...")
    stream = CommonTokenStream(lexer)
    
    print("Parsing tokens...")
    parser = penguinParser(stream)
    
    print("Creating parse tree...")
    tree = parser.program()
    
    print(tree.toStringTree(recog=parser)) if p else None
    
    return tree


def abstact_syntax_tree(cst: str):
    """Creates an abstract syntax tree (AST) from the concrete syntax tree (CST).
    
    CST -> AST

    Args:
        cst (str): The concrete syntax tree (CST).
    """

    print("Generating abstract syntax tree...")
    
    ast_gen = ASTGenerator()
    tree: ASTNode = ast_gen.visit(cst)
    
    return tree
    

def typed_abstact_syntax_tree(ast: str):
    """Creates a type annotated abstract syntax tree (TAST) from the abstract syntax tree (AST).
    
    AST -> TAST

    Args:
        ast (str): The abstract syntax tree (AST).
    """
    
    print("Generating typed abstract syntax tree...")
    
    typechecker = TypeChecker()
    tree = typechecker.check_program(tree)
    
    return tree

def print_tree(tree: str) -> None:
    """Prints the tree in a readable format.
    
    Args:
        tree (str): The tree to print.
    """
    
    print("########### JSON STARTS HERE ###########")
    print(json.dumps(tree, cls=ASTEncoder, indent=2))
    print("############ JSON ENDS HERE ############")


def main(input_file: str, output_file: str = "out.gb"):
    """main logic for the compiler."""
    
    input_stream: str = read_input_file(input_file)
    
    # Frontend
    
    cst: str = concrete_syntax_tree(input_stream)
    ast: ASTNode = abstact_syntax_tree(cst)
    taast: str = typed_abstact_syntax_tree(ast)
    
    # Backend
    # RGBDS
    # RGBASM to binary
    # Cleanup


if __name__ == "__main__":
    main("examples/arkanoid.peg", "out.gb")
