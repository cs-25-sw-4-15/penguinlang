"""File containing the CLI for the project.

Written with Typer.

Info til gruppemedlemmer fra Naitsa:
    Dokumentationen jeg følger for at lave CLI'en er her:
    https://typer.tiangolo.com

Usage:
    py src/cli.py COMMAND [OPTIONS] ...

Help:
    py src/cli.py --help
    py src/cli.py COMMAND --help
"""

import sys
import os
from pathlib import Path

# add the src directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import compiler functions
from src.compiler import write_output_file, print_tree, read_input_file, concrete_syntax_tree, \
    abstact_syntax_tree, typed_annotated_abstact_syntax_tree, \
    intermediate_representation, register_allocation, code_generation, \
    compile_rgbasm, full_compile

# Import the necessary modules
import typer
from typing_extensions import Annotated

# Create instance of Typer
app = typer.Typer()


# Define the command line interface (CLI) for the project
@app.command()
def compile(input_path: Annotated[str, typer.Argument(help="Input file path")], 
            output_path: Annotated[str, typer.Argument(help="Output file path")] = "out.gb"):
    print(input_path)
    print(output_path)


@app.command()
def test():
    print("Test function called")


@app.command()
def cst(input_path: Annotated[str, typer.Argument(help="Input file path")]):
    print("AST function called with input:", input_path)
    
    input_stream = read_input_file(input_path)
    cst = concrete_syntax_tree(input_stream, p=True)
    print("made cst : " + type(cst))
    

@app.command()
def ast(input_path: Annotated[str, typer.Argument(help="Input file path")]):
    print("AST function called with input:", input_path)
    
    input_stream = read_input_file(input_path)
    cst = concrete_syntax_tree(input_stream)
    ast = abstact_syntax_tree(cst)
    print_tree(ast)


@app.command()
def taast(input_path: Annotated[str, typer.Argument(help="Input file path")]):
    print("Typed AST function called with input:", input_path)
    
    input_stream = read_input_file(input_path)
    cst = concrete_syntax_tree(input_stream)
    ast = abstact_syntax_tree(cst)
    taast = typed_annotated_abstact_syntax_tree(ast)
    
    print_tree(taast)


@app.command()
def ir(input_path: Annotated[str, typer.Argument(help="Input file path")]):
    print("Generating IR for input:", input_path)
    
    input_stream = read_input_file(input_path)
    cst = concrete_syntax_tree(input_stream)
    ast = abstact_syntax_tree(cst)
    taast = typed_annotated_abstact_syntax_tree(ast)
    ir = intermediate_representation(taast)
    
    print("IR STARTS HERE")
    print(ir)  # This will call __str__ on the IRProgram object
    print("DONE")


@app.command()
def ra(input_path: Annotated[str, typer.Argument(help="Input file path")]):
    print("Generating IR for input:", input_path)
    
    input_stream = read_input_file(input_path)
    cst = concrete_syntax_tree(input_stream)
    ast = abstact_syntax_tree(cst)
    taast = typed_annotated_abstact_syntax_tree(ast)
    ir = intermediate_representation(taast)
    ra = register_allocation(ir)
    
    print("RA STARTS HERE")
    print(ra)  # This will call __str__ on the IRProgram object
    print("DONE")

@app.command()
def codegen(input_path: Annotated[str, typer.Argument(help="Input file path")], 
            output_path: Annotated[str, typer.Argument(help="Output file path")] = "out.asm"):
    print("Generating code for input:", input_path)    
    input_stream = read_input_file(input_path)
    cst = concrete_syntax_tree(input_stream)
    ast = abstact_syntax_tree(cst)
    taast = typed_annotated_abstact_syntax_tree(ast)
    ir = intermediate_representation(taast)
    ra = register_allocation(ir)
    rgbasm_code = code_generation(ra)
    
    output_dir = Path(output_path).parent
    write_output_file(f"{output_dir}/main.asm", rgbasm_code)
    


@app.command()
def compile(input_path: Annotated[str, typer.Argument(help="Input file path")],
            output_path: Annotated[str, typer.Argument(help="Output file path")] = "out.gb"):
    full_compile(input_path, output_path, True)
    

if __name__ == "__main__":
    # Run the CLI application
    app()
