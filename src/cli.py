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
import json




# Import the necessary modules
import typer
from typing_extensions import Annotated
from ast_classes import ASTNode
from asttype_checker import TypeChecker

# Import compiler functions
from compiler import read_input_file, \
    concrete_syntax_tree, abstact_syntax_tree

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
    print("JSON STARTS HERE")
    print(json.dumps(ast, cls=ASTEncoder))


@app.command()
def taast(input_path: Annotated[str, typer.Argument(help="Input file path")]):
    print("Typed AST function called with input:", input_path)
    input_stream = read_input_file(input_path)
    cst = concrete_syntax_tree(input_stream)
    ast = abstact_syntax_tree(cst)
    typechecker = TypeChecker()
    typechecker.check_program(ast)
    print("JSON STARTS HERE")
    print(json.dumps(ast, cls=ASTEncoder))
    print("DONE")

if __name__ == "__main__":
    # Run the CLI application
    app()
