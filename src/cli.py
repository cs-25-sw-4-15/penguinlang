""" """
Denne fil indeholder CLI'en for compileren. 
Denne fil er ansvarlig for at parse argumenter og kalde compileren med de rigtige argumenter.
"""

# normoal modules
import sys
import typer # typer til at lave CLI


app = typer.Typer() # Opretter en ny CLI

@app.command()
def compile(input_file: str, output_file: str = "out.gb"):
    
    input_stream = FileStream(input_file)
    lexer = ExprLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ExprParser(stream)
    tree = parser.start_()
    
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
    app() # Kør CLI'en """