"""Penguin Compiler

Containes the main logic for the compiler.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import json
import subprocess
from pathlib import Path

# antlr4 modules
from antlr4 import FileStream, CommonTokenStream

# antl4 generated modules
from src.generated.penguinLexer import penguinLexer
from src.generated.penguinParser import penguinParser

# custom modules
from src.astClasses import ASTNode
from src.astGenerator import ASTGenerator
from src.astTypeChecker import TypeChecker
from src.IRProgram import IRGenerator, IRProgram
from src.RegisterAllocator import RegisterAllocator
from src.codegen import CodeGenerator

# logging
from src.logger import logger


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


def write_output_file(output_file: str, data: str, p: bool = False):
    """Writes the output data to a file.
    
    Args:
        output_file (str): The path to the output file.
        data (str): The data to write to the file.
    """
    
    if not p: print("Writing output file...")
    
    with open(output_file, "w") as f:
        f.write(data)
    
    if not p: print(f"Output written to {output_file}")    


def print_tree(tree: ASTNode, p: bool = False):
    """Prints the tree in a readable format.
    
    Args:
        tree (ASTNode): The tree to print.
    """
    
    print("JSON STARTS HERE")
    print(json.dumps(tree, cls=ASTEncoder, indent=4))
    print("JSON ENDS HERE")


def read_input_file(input_file: str, p: bool = False):
    """Reads the input file and returns a FileStream.
    
    Args:
        input_file (str): The path to the input file.
    """
    
    if not p: print("Reading file...")
    
    return FileStream(input_file, encoding="utf-8")


def concrete_syntax_tree(input_stream: str, p: bool = False):
    """Creates a concrete syntax tree (CST) from the input stream.
    
    Lexing -> tokenstresm -> parsing -> parse tree (CST)
    
    Args:
        input_stream (str): The input stream to parse.
        
    Returns:
        tree (str): The parse tree (CST).
    """
    
    if not p: print("Lexing file...")
    lexer = penguinLexer(input_stream)
    
    if not p: print("Creating token stream...")
    stream = CommonTokenStream(lexer)
    
    if not p: print("Parsing tokens...")
    parser = penguinParser(stream)
    
    if not p: print("Creating parse tree...")
    tree = parser.program()
    
    if not p: print(tree.toStringTree(recog=parser)) if p else None
    
    return tree


def abstact_syntax_tree(cst: str, p: bool = False):
    """Creates an abstract syntax tree (AST) from the concrete syntax tree (CST).
    
    CST -> AST

    Args:
        cst (str): The concrete syntax tree (CST).
    """

    if not p: print("Generating abstract syntax tree...")
    
    ast_gen = ASTGenerator()
    tree: ASTNode = ast_gen.visit(cst)
    
    return tree
    

def typed_annotated_abstact_syntax_tree(ast: ASTNode, p: bool = False):
    """Creates a type annotated abstract syntax tree (TAST) from the abstract syntax tree (AST).
    
    AST -> TAST

    Args:
        ast (str): The abstract syntax tree (AST).
    """
    
    if not p: print("Generating typed abstract syntax tree...")
    
    tree = ast
    typechecker = TypeChecker()
    typechecker.check_program(tree)
    
    return tree


def intermediate_representation(taast: ASTNode, p: bool = False):
    """Generates the intermediate representation (IR) from the typed abstract syntax tree (TAST).
    
    TAST -> IR
    
    Args:
        taast (ASTNode[List]): The typed abstract syntax tree (TAST).
    """
    
    if not p: print("Generating intermediate representation...")
    
    ir_generator = IRGenerator()
    ir_program: IRProgram = ir_generator.generate(taast)
    
    return ir_program
    

def register_allocation(ir_program: IRProgram, num_registers: int = 4, p: bool = False):
    """Generates the register allocation for the intermediate representation (IR).
    
    IR -> RA
    
    Args:
        ir_program (IRProgram): The intermediate representation (IR).
    """
    
    if not p: print("Allocating registers...")
    
    reg_alloc = RegisterAllocator(num_registers=num_registers)
    ra_program: IRProgram = reg_alloc.allocate_registers(ir_program)
    
    return ra_program


def code_generation(ra_program: IRProgram, p: bool = False):
    """Generates the final code from the register allocated intermediate representation (IR).
    
    RA -> Code
    
    Args:
        ra_program (IRProgram): The register allocated intermediate representation (IR).
    """
    if not p: print("Generating code...")
    
    codegen = CodeGenerator()
    rgbasm_code = codegen.generate_code(ra_program)
    
    return rgbasm_code


def compile_rgbasm(rgbasm_code: str, output_file: str = "out.gb", p: bool = False):
    """Compiles the RGBASM code to binary.

    Args:
        rgbasm_code (str): The RGBASM code to compile.
        output_file (str): The output file path.
    """

    if not p: print("Compiling RGBASM code to binary...")

    output_dir = Path(output_file).parent
    output_dir.mkdir(parents=True, exist_ok=True)  # Ensure the output directory exists

    write_output_file(f"{output_dir}/main.asm", rgbasm_code, p=p)

    # Use the system PATH to locate rgbds tools
    try:
        subprocess.run(["rgbasm", "-o", f"{output_dir}/output.o", f"{output_dir}/main.asm"], check=True)
        subprocess.run(["rgblink", "-o", output_file, f"{output_dir}/output.o"], check=True)
        subprocess.run(["rgbfix", "-v", "-p", "0xFF", output_file], check=True)
    except FileNotFoundError as e:
        print(f"Error: {e}. Ensure the RGBDS tools are installed and available in your PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error during compilation: {e}")


def full_compile(input_file: str, output_file: str = "out.gb", p: bool = False):
    """Full compile process from input file to output file.
    
    Args:
        input_file (str): The input file path.
        output_file (str): The output file path.
    """
    
    if not p: print("Compiling...")
    
    main(input_file, output_file, p=p)
    
    if not p: print("Compilation finished.")


def main(input_file: str, output_file: str = "out.gb", p: bool = False):
    """main logic for the compiler."""
    
    input_stream: str = read_input_file(input_file, p=p)
    
    # Frontend
    
    cst = concrete_syntax_tree(input_stream, p=p)
    
    ast = abstact_syntax_tree(cst, p=p)
    
    taast = typed_annotated_abstact_syntax_tree(ast, p=p)
    
    # Backend
    
    ir = intermediate_representation(taast, p=p)
    
    ra = register_allocation(ir, p=p)
    
    rgbasm_code = code_generation(ra, p=p)
    
    # Compile to binary
        
    compile_rgbasm(rgbasm_code, output_file, p=p)


if __name__ == "__main__":
    main("examples/arkanoid.peg", "out.gb")
