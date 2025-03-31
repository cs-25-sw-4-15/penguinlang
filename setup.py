"""
Denne fil indeholder CLI'en for compileren. 
Denne fil er ansvarlig for at parse argumenter og kalde compileren med de rigtige argumenter.
"""

import typer # typer til at lave CLI

app = typer.Typer() # Opretter en ny CLI

@app.command()
def compile(input_file: str, output_file: str = "out.gb"):
    pass

if __name__ == "__main__":
    app() # Kør CLI'en