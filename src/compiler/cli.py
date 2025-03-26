"""
Denne fil indeholder CLI'en for compileren. 
Denne fil er ansvarlig for at parse argumenter og kalde compileren med de rigtige argumenter.
"""

import typer # typer til at lave CLI
from compiler import parser, codegen

app = typer.Typer() # Opretter en ny CLI

@app.command()
def compile(input_file: str, output_file: str = "out.gb"):
    # read file
    source: str = ""
    with open(input_file, "r") as file:
        # Open recource context and read the file
        source = file.read()
    
    typer.echo("Generating AST from input_file...")
    # ast = 
    
    typer.echo("Generating RGBASM code...")
    # asm_code = 
    
    typer.echo("Writing to file...")
    with open("out.asm", "w") as file:
        # Open recource context and write the file
        #file.write(asm_code)
        pass
    
    # RGBASM to binary
    typer.echo("Compiling to Game Boy ROM...")
    typer.run([f"scripts/build.sh {"out.asm"} {output_file}"])
              
    # cleanup
    #typer.echo("Cleanup...")
    #typer.run([f"scripts/cleanup.sh"])
    
    typer.echo("Done! Output file: " + output_file)
    
    
if __name__ == "__main__":
    app() # Kør CLI'en