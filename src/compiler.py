"""Penguin Compiler

Containes the main logic for the compiler.
"""

import json
from typing import List

# antlr4 modules
from antlr4 import FileStream, CommonTokenStream


# antl4 generated modules
from generated.penguinLexer import penguinLexer
from generated.penguinParser import penguinParser

# custom modules
from ast_classes import ASTNode
from ast_generator import ASTGenerator
from asttype_checker import TypeChecker
from IRProgram import IRGenerator, IRProgram
from RegisterAllocator import RegisterAllocator
from codegen import CodeGenerator


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


def print_tree(tree: ASTNode) -> None:
    """Prints the tree in a readable format.
    
    Args:
        tree (ASTNode): The tree to print.
    """
    
    print("JSON STARTS HERE")
    print(json.dumps(tree, cls=ASTEncoder, indent=4))
    print("JSON ENDS HERE")


def read_input_file(input_file: str) -> FileStream:
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


def abstact_syntax_tree(cst: str, p: bool = False) -> ASTNode[List]:
    """Creates an abstract syntax tree (AST) from the concrete syntax tree (CST).
    
    CST -> AST

    Args:
        cst (str): The concrete syntax tree (CST).
    """

    print("Generating abstract syntax tree...")
    
    ast_gen = ASTGenerator()
    tree: str = ast_gen.visit(cst)
    
    return tree
    

def typed_annotated_abstact_syntax_tree(ast: ASTNode[List], p: bool = False) -> ASTNode[List]:
    """Creates a type annotated abstract syntax tree (TAST) from the abstract syntax tree (AST).
    
    AST -> TAST

    Args:
        ast (str): The abstract syntax tree (AST).
    """
    
    print("Generating typed abstract syntax tree...")
    
    tree = ast
    typechecker = TypeChecker()
    typechecker.check_program(tree)
    
    return tree


def intermediate_representation(taast: ASTNode[List], p: bool = False) -> IRProgram:
    """Generates the intermediate representation (IR) from the typed abstract syntax tree (TAST).
    
    TAST -> IR
    
    Args:
        taast (ASTNode[List]): The typed abstract syntax tree (TAST).
    """
    
    print("Generating intermediate representation...")
    
    ir_generator = IRGenerator()
    ir_program: IRProgram = ir_generator.generate(taast)
    
    return ir_program
    

def register_allocation(ir_program: IRProgram, num_registers: int = 4, p: bool = False) -> IRProgram:
    """Generates the register allocation for the intermediate representation (IR).
    
    IR -> RA
    
    Args:
        ir_program (IRProgram): The intermediate representation (IR).
    """
    
    print("Allocating registers...")
    
    reg_alloc = RegisterAllocator(num_registers=num_registers)
    ra_program: IRProgram = reg_alloc.allocate(ir_program)
    
    return ra_program


def code_generation(ra_program: IRProgram, p: bool = False) -> str:
    """Generates the final code from the register allocated intermediate representation (IR).
    
    RA -> Code
    
    Args:
        ra_program (IRProgram): The register allocated intermediate representation (IR).
    """
    
    print("Generating code...")
    
    codegen = CodeGenerator()
    rgbasm_code = codegen.generate_code(ra_program)
    
    return rgbasm_code


def main(input_file: str, output_file: str = "out.gb") -> None:
    """main logic for the compiler."""
    
    input_stream: str = read_input_file(input_file)
    
    # Frontend
    
    cst = concrete_syntax_tree(input_stream)
    
    ast = abstact_syntax_tree(cst)
    
    taast = typed_annotated_abstact_syntax_tree(ast)
    
    # Backend
    
    ir = intermediate_representation(taast)
    
    ra = register_allocation(ir)
    
    rgbasm_code = code_generation(ra)
    
    # Compile RGBASM code to binary


if __name__ == "__main__":
    main("examples/arkanoid.peg", "out.gb")
