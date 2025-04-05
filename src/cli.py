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
    print("AST function called")


@app.command()
def ast(input_path: Annotated[str, typer.Argument(help="Input file path")]):
    print("AST function called")


@app.command()
def tast(input_path: Annotated[str, typer.Argument(help="Input file path")]):
    print("Typed AST function called")


if __name__ == "__main__":
    # Run the CLI application
    app()
