
# normoal modules
import sys
import os
import argparse

# antlr4 modules
from antlr4 import FileStream, CommonTokenStream
#from antlr4.tree import ParseTreeVisitor

# antl4 generated modules
from generated.penguinLexer import penguinLexer
from generated.penguinParser import penguinParser
from generated.penguinListener import penguinListener

# custom modules
""" from parser import parser
from codegen import codegen """

def main(input_file: str, output_file: str = "out.gb"):
    # read file
    print("Reading file...")
    input_stream = FileStream(input_file)
    # lex
    print("Lexing file...")
    lexer = penguinLexer(input_stream)
    # token stream
    print("Creating token stream...")
    stream = CommonTokenStream(lexer)
    # parse tokens
    print("Parsing tokens...")
    parser = penguinParser(stream)
    # parse tree
    print("Creating parse tree...")
    tree = parser.program()
    print("Done!")
    
    print(tree.toStringTree(recog=parser))
    
    # RGBASM to binary
    #typer.echo("Compiling to Game Boy ROM...")
    #typer.run([f"scripts/build.sh {"out.asm"} {output_file}"])
              
    # cleanup
    #typer.echo("Cleanup...")
    #typer.run([f"scripts/cleanup.sh"])
    
    #typer.echo("Done! Output file: " + output_file)
    
if __name__ == "__main__":
    argparse = argparse.ArgumentParser(description="Penguin Compiler")
    argparse.add_argument("input_file", help="Input file to compile")
    argparse.add_argument("-o", "--output_file", help="Output file to write to")
    args = argparse.parse_args()
    main(args.input_file, args.output_file)
