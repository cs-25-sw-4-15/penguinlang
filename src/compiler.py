"""Penguin Compiler

Containes the main logic for the compiler.
"""


# antlr4 modules
from antlr4 import FileStream, CommonTokenStream


# antl4 generated modules
from generated.penguinLexer import penguinLexer
from generated.penguinParser import penguinParser


# custom modules
from ast_generator import ASTGenerator


def read_input_file(input_file: str):
    """Reads the input file and returns a FileStream.
    
    Args:
        input_file (str): The path to the input file.
    """
    
    print("Reading file...")
    
    return FileStream(input_file, encoding="utf-8")


def concrete_syntax_tree(input_stream: str, p: bool = False) -> str:
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
    
    #tree: str = ASTGenerator().visit(cst)
    tree: str = ""
    
    return tree
    

def typed_abstact_syntax_tree(ast: str):
    """Creates a type annotated abstract syntax tree (TAST) from the abstract syntax tree (AST).
    
    AST -> TAST

    Args:
        ast (str): The abstract syntax tree (AST).
    """
    
    print("Generating typed abstract syntax tree...")
    
    tree: str = ""
    
    return tree


def main(input_file: str, output_file: str = "out.gb"):
    """main logic for the compiler."""
    
    input_stream: str = read_input_file(input_file)
    
    # Frontend
    
    cst = concrete_syntax_tree(input_stream)
    
    ast: str = abstact_syntax_tree(cst)
    
    tast: str = typed_abstact_syntax_tree(ast)
    
    # backend    
    # rgbds
    # cleanup
    # RGBASM to binary


if __name__ == "__main__":
    main("examples/arkanoid.peg", "out.gb")
