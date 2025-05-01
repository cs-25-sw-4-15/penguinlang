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

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import compiler functions
from src.compiler import print_tree, read_input_file, \
    concrete_syntax_tree, abstact_syntax_tree, typed_abstact_syntax_tree

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
    taast = typed_abstact_syntax_tree(ast)
    
    print_tree(taast)
    print(taast.statements[0])

if __name__ == "__main__":
    # Run the CLI application
    app()
