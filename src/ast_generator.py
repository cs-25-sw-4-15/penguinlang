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
    - context.name() : findes for at finde ud af hvilken geramamtik regl vej der er taget
    - visitExpressions() : håndterer besøg til flere børn i en node. spesifikt expressions grammatik reglen (expr expr expr)
    - 
"""


# Generated modules
from generated.penguinParser import penguinParser
from generated.penguinVisitor import penguinVisitor

# Custom modules
from ast_classes import ASTNode, \
    Program, \
    Declaration, Assignment, Initialization, ListInitialization, If, Loop, Return, ProcedureCallStatement, \
    UnaryOp, IntegerLiteral, StringLiteral, ProcedureCall, Variable, ListAccess, AttributeAccess, \
    ProcedureDef

# Typing modules
from typing import List, Any

# Logging modules
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ASTGenerator(penguinVisitor):
    """Converts an ANTLR parse tree into an AST.
    
    Konverterer en ANTLR parse tree til en AST.
    
    Args:
        penguinVisitor (class): The ANTLR visitor class for the Penguin language.
    """
    
    """Program"""
    
    def visitProgram(self, context: penguinParser.ProgramContext) -> Program:
        """Visits the program context and creates a Program AST node.
        
        Metoden besøger programmet i CST'en og konverterer det til en AST node.
        
        Args:
            context (penguinParser.ProgramContext): The program context from the ANTLR parse tree.
        
        Returns:
            Program: The AST node representing the program.
        """
        logger.debug("Visiting program")
        
        # Visit each statement in the program context
        statements: List[ASTNode] = [self.visit(stmt) for stmt in context.statement()]
        
        # Assert that all statements are ASTNodes
        assert all(isinstance(stmt, ASTNode) for stmt in statements), "Not all statements are ASTNodes"
        
        logger.debug(f"Program contains {len(statements)} statements")
        
        return Program(statements)
    
    """Statements"""

    def visitDeclaration(self, context: penguinParser.DeclarationContext) -> Declaration:
        """Visits the declaration context and creates a Declaration AST node.
        
        Visit declaration and create a Declaration AST node.

        Args:
            context (penguinParser.DeclarationContext): The declaration context from the ANTLR parse tree.

        Returns:
            Declaration: The AST node representing the declaration.
        """
        
        logger.debug(f"Visiting declaration: {context.getText()}")
        
        # Læg mærke til at for context.NOGET er noget havd det hedder i vores grammar regler!
        var_type: str = context.type().getText() # getText() returns token string
        name: str = context.name().getText()
        
        assert var_type and name, "Declaration missing type or name"
        
        logger.debug(f"Declared variable: {name} of type {var_type}")
        
        return Declaration(var_type, name)
    
    def visitAssignment(self, context: penguinParser.AssignmentContext) -> Assignment:
        """ Visits the assignment context and creates an Assignment AST node.
        
        Args:
            context (penguinParser.AssignmentContext): The assignment context from the ANTLR parse tree.
        
        Returns:
            Assignment: The AST node representing the assignment.
        """
        
        logger.debug(f"Visiting assignment: {context.getText()}")
        
        # Tjek om context navn findes for at vide om det er en list assignment 
        # eller en normal assignment - Altså, hvilken regl skal der følges
        if context.name():
            # Hvis det er en normal assignment
            target = self.visit(context.name())
        else:
            # Hvis det er en list assignment
            target = self.visit(context.list_access())
        
        # Besøg værdien af assignmenten
        value = self.visit(context.expression())
        
        return Assignment(target=target, value=value)

    def visitInitialization(self, context: penguinParser.InitializationContext) -> Initialization | ListInitialization:
        
        # Tjek typen af initializeren er en liste eller en normal
        if context.type_():
            # Hvis det er en normal initialization
            var_type: str = context.type_().getText()
            name: str = context.name().getText()
            value: str = self.visit(context.expression())
            return Initialization(var_type, name, value)
        elif context.LBRACK():
            # Check for "[" - navnet efter lexerens reglsæt 
            # Hvis det er liste initialization
            name: str = context.name().getText()
            values: list[ASTNode] = self.visit(context.expressions())
            return ListInitialization(name, values)
        else:
            # Error
            raise Exception("Unknown initialization type")
        
   
    def visitConditionalStatement(self, consitional: penguinParser.ConditionalStatementContext):
        pass
    
    def visitLoopStatement() -> Loop:
        pass
    
    def visitReturnStatement() -> Return:
        pass
    
    def visitProcedureCallStatement() -> ProcedureCallStatement:
        pass
    
    
    """ def visitProcedureCallStatement(self, context: penguinParser.ProcedureCallStatementContext) -> ProcedureCallStatement:
        logger.debug(f"Visiting procedure call statement: {context.getText()}")
        # See if the context has a procedure call
        proc_call_context = context.procedureCall()
        assert proc_call_context is not None, "Procedure call missing in statement"
        
        name_node: ASTNode = self.visit(proc_call_context.name())
        logger.debug(f"Procedure name: {name_node}")
        
        # Args start as an empty list per default
        arg_nodes: List[ASTNode] = []
        # Fill args if they exist
        if proc_call_context.argumentList():
            # Visit the argument list and get the expressions
            # This is done by entering the argumentList context from the procedureCall context
            # Which is bas shit crazy, but look though the classes, and it is there
            arg_nodes = [self.visit(arg) for arg in proc_call_context.argumentList().expression()]
            logger.debug(f"Procedure arguments: {arg_nodes}")
            
        return ProcedureCallStatement(name=name_node, args=arg_nodes) """
    
    
    """Expressions"""
    
    
    def visitExpression(self, context: penguinParser.ExpressionContext):
        pass
    
    def visitExpr_val(self, context: penguinParser.Expr_valContext):
        # Can probably be incorporated in where it is implemented
        pass
    
    def visitLiteral(self, context: penguinParser.LiteralContext) -> StringLiteral | IntegerLiteral:
        pass
    
    def visitName(self, context: penguinParser.NameContext) -> AttributeAccess | Variable | ListAccess:
        """Visits the name context and creates a Variable AST node.
        
        This is a thought peice of shit
        En grund til at dot notation nok ikke var så smart alligevel
        
        Men hvad sker der her????:
        - starter med at finde ud af hvad basis navnet er.
        - for hvrr attribut i navnet, wrappes der med en AttributeAccess node
        - for hver list accsess i navnet [...] wrapeps med ListAccess node, sammed nuværende node
        - der retuneres til sidst en variable node med det sidste navn og alle de wrapede nodes, det er meget nested (venstre til højre heldigvis) og det er forfærdeligt
        
        Args:
            context (penguinParser.NameContext): The name context from the ANTLR parse tree.
        
        Returns:
            Some ASTNode of type Variable, ListAccess or AttributeAccess.
            ¯\_(ツ)_/¯
            TODO: Find ud af hvad der faktisk retuneres her
        """
        
        logger.debug(f"Visiting name: {context.getText()}")
        assert context.IDENTIFIER(), "Name node has no identifiers"
        
        # Find basis navnet
        current_name_node: ASTNode = Variable(context.IDENTIFIER(0).getText())
        logger.debug(f"Base variable: {current_name_node}")
        
        # For hver attribut i navnet af den nuværende context, undtagen basis
        for i in range(1, len(context.IDENTIFIER())):
            # Wrap current_name_node med en AttributeAccess node (alt det der dot notation)
            current_name_node = AttributeAccess(current_name_node, context.IDENTIFIER(i).getText())
            logger.debug(f"Wrapped in AttributeAccess: {current_name_node}")
        
        # For hver list access i navnet
        for expression_context in context.expression():
            # Besøg listen og få fat i index expression, som er det der står i []
            index_expression: ASTNode = self.visit(expression_context)
            # Wrap current_name_node med en ListAccess node (alt det der bracket notation)
            current_name_node = ListAccess(current_name_node, index_expression)
            logger.debug(f"Wrapped in ListAccess: {current_name_node}")
        
        return current_name_node
    
    def visitListAccess(self, context: penguinParser.ListAccessContext) -> ListAccess:
        name_node = self.visit(context.name())
        indeces: List[ASTNode] = self.visitListOfNodes(context.expressions())
        return ListAccess(name=name_node, indeces=indeces)
    
    def visitAttributeAccess(self, context: penguinParser.AttributeAccessContext) -> AttributeAccess:
        name_node: ASTNode = self.visit(context.name())
        attribute: str = self.IDENTIFIER().getText()
        return AttributeAccess(name_node=name_node, attribute=attribute)
    
    def visitProcedureCall() -> ProcedureCall:
        pass
    
    
    """Visit Handlers"""
    
    
    def visitListOfNodes(self, context: penguinParser.ExpressionsContext) -> list[ASTNode]:
        """Handles the visit to multiple nodes in the CST.

        Args:
            context (penguinParser.ExpressionsContext): _description_

        Returns:
            list[ASTNode]: A list of AST nodes.
        """
        
        visited_exprs = [self.visit(expr) for expr in context.expression()]
        
        return visited_exprs
    
    def visitParameterList(self, context: penguinParser.ParameterListContext) -> list[ASTNode]:
        pass
    
    def visitArgumentList(self, context: penguinParser.ArgumentListContext) -> list[ASTNode]:
        pass
    
    def visitType(self, context: penguinParser.TypeContext) -> str:
        pass
    
    def visitStatementBlock(self, context: penguinParser.StatementBlockContext) -> list[ASTNode]:
        # Can probably be incorporated in where it is implemented
        pass
