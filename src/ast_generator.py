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
    AST: Program(statements=[Initialization(var_type='int', name='a', value=BinaryOp(left=IntegerLiteral(value=1), op='+', right=IntegerLiteral(value=2)))])
    
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
    Declaration, Assignment, Initialization, ListInitialization, Conditional, Loop, Return, ProcedureCallStatement, \
    BinaryOp, UnaryOp, IntegerLiteral, StringLiteral, ProcedureCall, Variable, ListAccess, AttributeAccess, \
    ProcedureDef

# Typing modules
from typing import List

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
        """
        
        logger.debug(f"Visiting declaration: {context.getText()}")
        
        # Læg mærke til at for context.NOGET er noget havd det hedder i vores grammar regler!
        var_type: str = context.type().getText() # getText() returns token string
        name: str = context.name().getText()
        
        assert var_type and name, "Declaration missing type or name"
        
        logger.debug(f"Declared variable: {name} of type {var_type}")
        
        return Declaration(var_type, name)
    
    def visitAssignment(self, context: penguinParser.AssignmentContext) -> Assignment:
        """ Visits the assignment context and creates an Assignment AST node."""
        
        logger.debug(f"Visiting assignment: {context.getText()}")
        
        # Tjek om context navn findes for at vide om det er en list assignment 
        # eller en normal assignment - Altså, hvilken regl skal der følges
        if context.name():
            # Hvis det er en normal assignment
            target = self.visit(context.name())
            logger.debug(f"Assignment target: {target}")
        else:
            # Hvis det er en list assignment
            target = self.visit(context.list_access())
            logger.debug(f"Assignment target list: {target}")
        
        # Besøg værdien af assignmenten
        value = self.visit(context.expression())
        
        assert target and value, "Assignment missing target or value"
        
        logger.debug(f"Assigment value: {value}, target: {target}")
        
        return Assignment(target=target, value=value)

    def visitInitialization(self, context: penguinParser.InitializationContext) -> Initialization | ListInitialization:
        
        logger.debug(f"Visiting initialization: {context.getText()}")
        
        # Tjek typen af initializeren er en liste eller en normal
        if context.type_():
            logger.debug("Normal initialization")
            
            # Hvis det er en normal initialization
            var_type: str = context.type_().getText()
            name: str = context.name().getText()
            value: str = self.visit(context.expression())
            
            assert var_type and name and value, "Initialization missing type, name or value"
            logger.debug(f"Initialization type: {var_type}, name: {name}, value: {value}")
            
            return Initialization(var_type, name, value)
        
        elif context.LBRACK():
            # Check for "[" - navnet efter lexerens reglsæt 
            # Hvis det er liste initialization
            logger.debug("List initialization")
            
            name: str = context.name().getText()
            values: list[ASTNode] = self.visit(context.expressions())
            
            assert name and values, "List initialization missing name or values"
            logger.debug(f"List initialization name: {name}, values: {values}")
            
            return ListInitialization(name, values)
        
        else:
            logger.error("Unknown initialization type")
            raise Exception("Unknown initialization type")
        
    def visitConditionalStatement(self, context: penguinParser.ConditionalStatementContext) -> Conditional:
        logger.debug(f"Visiting conditional statement: {context.getText()}")
        # TODO
        return super().visitConditionalStatement(context)
    
    def visitConditionalStatementElse(self, context: penguinParser.ConditionalStatementElseContext) -> Conditional:
        # Kan være det bare skal være del af conditional statement, da de bergge retuyreene conditional
        logger.debug(f"Visiting conditional statement else: {context.getText()}")
        # TODO
        return super().visitConditionalStatementElse(context)
    
    def visitLoop(self, context: penguinParser.LoopContext) -> Loop:
        logger.debug(f"Visiting loop: {context.getText()}")
        # TODO
        return super().visitLoop(context)
    
    def visitProcedureDeclaration(self, context: penguinParser.ProcedureDeclarationContext) -> ProcedureDef:
        # TODO
        return super().visitProcedureDeclaration(context)
    
    def visitReturnStatement(self, context: penguinParser.ReturnStatementContext) -> Return:
        logger.debug(f"Visiting return statement: {context.getText()}")
        # TODO
        return super().visitReturnStatement(context)
    
    def visitProcedureCallStatement(self, context: penguinParser.ProcedureCallStatementContext) -> ProcedureCallStatement:
        logger.debug(f"Visiting procedure call statement: {context.getText()}")
        # TODO
        return super().visitProcedureCallStatement(context)
    
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
    
    def visitExpression(self, context: penguinParser.ExpressionContext) -> BinaryOp | UnaryOp | ASTNode:
        """Visits the given expression as an BinaryOp, UnaryOp or visits a value from Expr_val (terminal value)
        
        Expressions kan enten være:
        - terminal værdier, hvilket er indikeret med ét navn/hvadend acesss, procedurecall eller sybere expression
        - unary operation, bestående af 2 child nodes
        - binary operation, ebstående af 3 child nodes
        
        EN ordenlig håndfuld, men overkommelig
        
        Hvis det ikke er casen, er det noget galt...
        
        Return:
            BinaryOp | UnaryOp | ASTNode
        """
        
        logger.debug(f"Visiting expression: {context.getText()}")
        
        # For the uninisiated, så er match i python switch i andre sprog. behøver ikke break
        match context.getChildCount():
            case 1:
                # Fidne om det er en værdi, expression osv.
                logger.debug("Expression has 1 child")
                return self.visit(context.expr_val())
            
            case 2:
                logger.debug("Expression has 2 childen i.e. UnaryOp")
                
                op = context.getChild(0).getText()
                right = self.visit(context.expression(0)) # first expression child
                
                assert op and right, "UnaryOp missing operator or right child"
                logger.debug(f"UnaryOp operator: {op}, right: {right}")
                
                return UnaryOp(op, right)
            
            case 3:
                logger.debug("Expression has 3 children i.e. BinaryOp")
                
                left = self.visit(context.expression(0)) # index 0 because it is the first child
                op = context.getChild(1).getText() # operator is the second child
                right = self.visit(context.expression(1)) # index 1 because it is the second child
                
                assert left and op and right, "BinaryOp missing left, operator or right child"
                logger.debug(f"BinaryOp left: {left}, operator: {op}, right: {right}")
                
                return BinaryOp(left, op, right)      
        
        # Something be wrong in these woods
        logger.error("Unknown expression type")
        raise Exception(f"Unknown expression type from {context.getText()}")
    
    def visitExpr_val(self, context: penguinParser.Expr_valContext) -> ASTNode:
        """Visits the expr_val context and creates an AST node.
        
        Forstil dig en verden af variabler, som alle er integers, og måske en streg
        Men hvordan er vi fundet frem til disse varabler? det ser vi på i denen episode af
        "Sebastian skal huske at skrive aaaaaalllle de forskellgie værdiskabende ekspressions ind
        
        reminder:
            : literal           // numre
            | name              // variabler
            | listAccess        // værdier i lister
            | procedureCall     // værdi af procedure
            | attributeAccess   // værdi af attribut i struct
            | LPAREN expression RPAREN // parenteser
        """
        # Can probably be incorporated in where it is implemented
        # Can også være dejligt med clean sepration
        logger.debug(f"Visiting expr_val: {context.getText()}")
        
        # vi prøver at finde ud af havd det nu er vi leger med, og så håndtere en anden funktion det derfra
        if context.literal():
            logger.debug("Visiting literal in expr_val")
            return self.visit(context.literal())
        elif context.name():
            logger.debug("Visiting name in expr_val")
            return self.visit(context.name())
        elif context.procedureCall():
            logger.debug("Visiting procedure call in expr_val")
            return self.visit(context.procedureCall())
        elif context.listAccess():
            logger.debug("Visiting list access in expr_val")
            return self.visit(context.listAccess())
        elif context.attributeAccess():
            logger.debug("Visiting attribute access in expr_val")
            return self.visit(context.attributeAccess())
        elif context.expression():
            logger.debug("Visiting expression in expr_val, - paran?")
            # Paranteser? nææ det er bare en expression som barn
            return self.visit(context.expression())
        
        # Can you small that? Rain is coming, pack up the picnic basket
        logger.error("Unknown expr_val type")      
        raise Exception(f"Unknown expr_val type from {context.getText()}") 
    
    def visitLiteral(self, context: penguinParser.LiteralContext) -> IntegerLiteral | StringLiteral:
        """Visits the literal context and creates an AST node (Finally).
        
        Forstil dig en verden af variabler, som alle er integers, og måske en streg
        Men henne gang kan det være skreven med hiroglyffer eller noget andet
        
        kig i visitLiteral classen for at finde ud af hvad der sker
        """
        logger.debug(f"Visiting literal: {context.getText()}")
        
        if context.DECIMAL():
            value = int(context.DECIMAL().getText())
            assert value is not None, "Integer literal is None"
            logger.debug(f"Integer literal: {value}")
            return IntegerLiteral(value)
        elif context.HEX():
            value = int(context.HEX().getText(), 16) # convert to int from binary
            assert value is not None, "Hex literal is None"
            logger.debug(f"Hex literal: {value}")
            return IntegerLiteral(value)
        elif context.BINARY():
            value = int(context.BINARY().getText(), 2) # convert to int from binary
            assert value is not None, "Binary literal is None"
            logger.debug(f"Binary literal: {value}")
            return IntegerLiteral(value)
        elif context.STRING():
            value = context.STRING().getText()
            assert value is not None, "String literal is None"
            logger.debug(f"String literal: {value}")
            return StringLiteral(value)
        
        logger.error("Unknown literal type")
        raise Exception(f"Unknown literal type from {context.getText()}")
    
    def visitName(self, context: penguinParser.NameContext) -> AttributeAccess | Variable | ListAccess:
        """Visits the name context and creates a Variable AST node.
        
        This is a thought peice of shit
        En grund til at dot notation nok ikke var så smart alligevel
        
        Men hvad sker der her????:
        - starter med at finde ud af hvad basis navnet er.
        - for hvrr attribut i navnet, wrappes der med en AttributeAccess node
        - for hver list accsess i navnet [...] wrapeps med ListAccess node, sammed nuværende node
        - der retuneres til sidst en variable node med det sidste navn og alle de wrapede nodes, det er meget nested (venstre til højre heldigvis) og det er forfærdeligt
        
        Returns:
            Some ASTNode of type Variable, ListAccess or AttributeAccess.
            ¯\\_(ツ)_/¯
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
        logger.debug(f"Visiting list access: {context.getText()}")
        
        name_node = self.visit(context.name())
        indeces: List[ASTNode] = self.visitExpressions(context.expressions())
        
        assert name_node and indeces, "List access missing name or indeces"
        logger.debug(f"List access name: {name_node}, indeces: {indeces}")
        
        return ListAccess(name=name_node, indeces=indeces)
    
    def visitAttributeAccess(self, context: penguinParser.AttributeAccessContext) -> AttributeAccess:
        logger.debug(f"Visiting attribute access: {context.getText()}")
        
        name_node: ASTNode = self.visit(context.name())
        attribute: str = self.IDENTIFIER().getText()
        
        assert name_node and attribute, "Attribute access missing name or attribute"
        logger.debug(f"Attribute access name: {name_node}, attribute: {attribute}")
        
        return AttributeAccess(name_node=name_node, attribute=attribute)
    
    def visitProcedureCall(self, context: penguinParser.ProcedureCallContext) -> ProcedureCall:
        logger.debug(f"Visiting procedure call: {context.getText()}")
        
        name = self.visit(context.name())
        # Ternary: hvis der er argumenter, så besøg dem og lav en liste af dem
        args = self.visit(context.argumentList()) if context.argumentList() else []
        
        return ProcedureCall(name, args)
    
    """Visit Handlers
    
    En masse af det samme, men det ser pænere ud
    """
    
    def visitExpressions(self, context: penguinParser.ExpressionsContext) -> list[ASTNode]:
        """Handles the visit to multiple expressions in the CST."""
        
        logger.debug(f"Visiting list of nodes: {context.getText()}")
        
        visited_exprs = [self.visit(expr) for expr in context.expression()]
        
        # isinstandce tjekker at et objekt X er af typen Y
        # all generere en liste af bolske værdier ud fra en for in generator
        assert all(isinstance(expr, ASTNode) for expr in visited_exprs), "Not all expressions are ASTNodes"
        logger.debug(f"Visited expressions: {visited_exprs}")
        
        return visited_exprs
    
    def visitParameterList(self, context: penguinParser.ParameterListContext) -> List[tuple[str, str]]:
        """Handles the visit to multiple parameters in the CST.
        
        Skal bruges til at generere AST'en for en procedure declaration
        """
        
        logger.debug(f"Visiting parameter list: {context.getText()}")
        
        # Visit each parameter in the parameter list
        parametres: List[ASTNode] = []
        
        """
        Hvis du ikke kender Zip metoden (class dims), er det ligt ligesom en lynlås for lister.
        Tager en mægnde lister af samme størrelkse og pair listindekserne sammen så man ender med en masse små lister
        
        Eksempel:
        https://www.w3schools.com/python/ref_func_zip.asp
        
        a = ("John", "Charles", "Mike")
        b = ("Jenny", "Christy", "Monica")
        x = zip(a, b)
        print(tuple(x)) # tuple gør edt ligt mere lækkert at se på
        
        output: (('John', 'Jenny'), ('Charles', 'Christy'), ('Mike', 'Monica')) 
        """
        
        # Zip de to lister sammen, så vi kan få fat i type og navn på samme tid
        for t, i in zip(context.type(), context.IDENTIFIER()):
            # Besøg type og navn og lav en ny node Variable for hver parameter
            parametres.append(Variable(i.getText(), t.getText()))
        
        assert all(isinstance(param, ASTNode) for param in parametres), "Not all parameters are ASTNodes"
        logger.debug(f"Parameter list: {parametres}")
        
        return parametres # liste af en typle af to strenge
    
    def visitArgumentList(self, context: penguinParser.ArgumentListContext) -> List[ASTNode]:
        logger.debug(f"Visiting argument list: {context.getText()}")
        
        # Arguments could could all come in some form of expression
        arguments: List[ASTNode] = [self.visit(expression) for expression in context.expression()]
        
        assert all(isinstance(arg, ASTNode) for arg in arguments), "Not all arguments are ASTNodes"
        logger.debug(f"Argument list: {arguments}")
        
        return arguments
    
    def visitType(self, context: penguinParser.TypeContext) -> str:
        # ved ikk endnu om denen overhoved behøves at blvie implementeret
        # men den er der under visitor pattern koden
        logger.debug(f"Visiting type: {context.getText()}")
        return super().visitType(context)
    
    def visitStatementBlock(self, context: penguinParser.StatementBlockContext) -> List[ASTNode]:
        # Can probably be incorporated in where it is implemented, præcist det samme some ovenover
        logger.debug(f"Visiting statement block: {context.getText()}")
        statmwetns: List[ASTNode] = [self.visit(statement) for statement in context.statement()]
        assert all(isinstance(stmt, ASTNode) for stmt in statmwetns), "Not all statements are ASTNodes"
        logger.debug(f"Statement block: {statmwetns}")
        return statmwetns
