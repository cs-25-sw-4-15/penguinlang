"""AST Generator for Penguin Language 

Generates AST by walking with the ANTLR4 generated visitor pattern 
and self-made AST classes on a CFT.


Note til gruppemedlemmer fra Naitsa:
    For at generere AST'en skal man bruge AST node classes og ANTLR4 visitor pattern.
    Så skal der bygges en AST Builder/generator med penguinVisitor.
    Med denne skal hver node i CST besøges og konverteres til en AST node.
    Dette gøres ved at definere en funktion for hver node type i CST'en.
    Hver node type i CST'en skal have en tilsvarende AST node class. Dem har vi.
    
    CST er meget detaljeret og AST er mere abstrakt.
    CST er en parse tree og AST er en syntax tree.
    
    Eksempel:
    Kode: int a = 1 + 2;
    CST: (program (statement (initialization (type int) (name a) = (expression (expression (expr_val (literal 1))) + (expression (expr_val (literal 2)))) ;)))
    AST: Initialization(type='int', name='a', value=BinaryOp('+', Number(1), Number(2)))
    
    Af de to er der en der er betydligt sjovere at lege med
    
    
    Metohder og navne i denen fil:
    - context : er det sted vi er i vores parse tree lige nu, havd vi kigger på
    - context.getText() : er det der står i den node vi kigger på, den rå string
    - self.visit(context.child) : besøger et barn af noden rekursivt
    - ASTNode return : V returnere vores egen node i stedet for ANTLR's node
"""


# Generated modules
from generated.penguinParser import penguinParser
from generated.penguinVisitor import penguinVisitor

# Custom modules
from ast_classes import ASTNode, \
    Program, \
    Declaration, Assignment, Initialization, ListInitialization, If, Loop, Return, ProcedureCallStatement, \
    UnaryOp, IntegerLiteral, StringLiteral, Variable, ListAccess, AttributeAccess, \
    ProcedureDef

# Typing modules
from typing import List, Any


class ASTGenerator(penguinVisitor):
    """Converts an ANTLR parse tree into an AST.
    
    Konverterer en ANTLR parse tree til en AST.
    
    Args:
        penguinVisitor (class): The ANTLR visitor class for the Penguin language.
    """
    
    def visitProgram(self, context: penguinParser.ProgramContext) -> Program:
        """Visits the program context and creates a Program AST node.
        
        Metoden besøger programmet i CST'en og konverterer det til en AST node.
        
        Args:
            context (penguinParser.ProgramContext): The program context from the ANTLR parse tree.
        
        Returns:
            Program: The AST node representing the program.
        """
        
        # Visit each statement in the program context
        statements: List[ASTNode] = [self.visit(statement) for statement in context.statement()]
        
        return Program(statements)

    def visitDeclaration(self, context: penguinParser.DeclarationContext) -> Declaration:
        """Visits the declaration context and creates a Declaration AST node.
        
        Visit declaration and create a Declaration AST node.

        Args:
            context (penguinParser.DeclarationContext): The declaration context from the ANTLR parse tree.

        Returns:
            Declaration: The AST node representing the declaration.
        """
        # Læg mærke til at for context.NOGET er noget havd det hedder i vores grammar regler!
        var_type: str = context.type().getText() # getText() returns token string
        name: str = context.name().getText()
        return Declaration(var_type, name)
    
    def visitAssignment(self, context: penguinParser.AssignmentContext) -> Assignment:
        """ Visits the assignment context and creates an Assignment AST node.
        
        Args:
            context (penguinParser.AssignmentContext): The assignment context from the ANTLR parse tree.
        
        Returns:
            Assignment: The AST node representing the assignment.
        """
        
        pass
