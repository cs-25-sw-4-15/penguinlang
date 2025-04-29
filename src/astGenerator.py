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
    AST: Program(statements=[Initialization(type_='int', name='a', value=BinaryOp(left=IntegerLiteral(value=1), op='+', right=IntegerLiteral(value=2)))])
    
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
from src.generated.penguinParser import penguinParser
from src.generated.penguinVisitor import penguinVisitor

# Custom modules
from src.astClasses import *
from src.customErrors import *

# Typing modules
from typing import List, Tuple, Union, Any 

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
        logger.info("Visiting program")
        
        # Visit each statement in the program context
        statements: List[ASTNode] = self.statementsToASTNodes(context.statement())
        
        # Assert that all statements are ASTNodes
        assert all(isinstance(stmt, ASTNode) for stmt in statements), "Not all statements in the block are ASTNodes" + "\n" + str(statements)
        
        logger.debug(f"Program contains {len(statements)} statements")
        
        return Program(statements)
    
    def statementsToASTNodes(self, statements: List[Any]) -> List[ASTNode]:
        """Takes parse tree list and goes thoug all root statemetns, visiting each and returning a list of AST nodes."""
        
        logger.info("Visiting list of statements.")
        
        visited_statements: List[ASTNode] = [self.visit(stmt) for stmt in statements]
        
        assert all(isinstance(stmt, ASTNode) for stmt in visited_statements), "Not all statements are ASTNodes" + "\n" + str(visited_statements)
        logger.debug(f"Visited statements: {visited_statements}")
        
        return visited_statements
    
    """Statements"""
    
    def visitDeclaration(self, context: penguinParser.DeclarationContext) -> Declaration:
        """Visits the declaration context and creates a Declaration AST node.
        
        Visit declaration and create a Declaration AST node.
        """
        
        logger.info(f"Visiting declaration: {context.getText()}")
        
        # Læg mærke til at for context.NOGET er noget havd det hedder i vores grammar regler!
        type_: str = context.type_().getText() # getText() returns token string
        name: str = context.name().getText()
        
        assert type_ and name, "Declaration missing type or name"
        
        logger.debug(f"Declared variable: {name} of type {type_}")
        
        return Declaration(type_, name)
    
    def visitAssignment(self, context: penguinParser.AssignmentContext) -> Assignment:
        """ Visits the assignment context and creates an Assignment AST node."""
        
        logger.info(f"Visiting assignment: {context.getText()}")
        
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

    def visitInitialization(self, context: penguinParser.InitializationContext) -> Union[Initialization, ListInitialization]:
        """Visits the initialization context and creates an Initialization or ListInitialization AST node."""
        
        logger.info(f"Visiting initialization: {context.getText()}")
        
        # Tjek typen af initializeren er en liste eller en normal
        if context.type_():
            logger.debug("Normal initialization")
            
            # Hvis det er en normal initialization
            type_: str = context.type_().getText()
            name: str = context.name().getText()
            value: str = self.visit(context.expression())
            
            assert type_ and name and value, "Initialization missing type, name or value"
            logger.debug(f"Initialization type: {type_}, name: {name}, value: {value}")
            
            return Initialization(type_, name, value)
        
        elif context.LBRACK():
            # Check for "[" - navnet efter lexerens reglsæt 
            # Hvis det er liste initialization
            logger.debug("List initialization")
            
            name: str = context.name().getText()
            values: list[ASTNode] = self.visitExpressions(context.expressions()) # list of expressions be like ~(_8^(I)
            
            assert name and values, "List initialization missing name or values"
            logger.debug(f"List initialization name: {name}, values: {values}")
            
            return ListInitialization(name, values)
        
        else:
            logger.error("Unknown initialization type encountered")
            raise UnknowninitializationTypeError("Unknown initialization type encountered")
        
    def visitConditionalStatement(self, context: penguinParser.ConditionalStatementContext) -> Conditional:
        """Visits the conditional statement context and creates a Conditional AST node."""
        
        logger.info(f"Visiting conditional statement: {context.getText()}")
        
        condition: ASTNode = self.visit(context.expression()) # condition er den eneste expression
        then_stmts: List[ASTNode] = self.visit(context.statementBlock()) # første block
        
        assert condition and then_stmts, "Conditional statement missing condition or statements"
        
        # Hvis der er en else statement skal den også besøges
        else_stmts: List[ASTNode] = None
        if context.conditionalStatementElse():
            else_stmts: List[ASTNode] = self.visit(context.conditionalStatementElse())
            
            assert else_stmts, "Conditional statement else missing statements"
            logger.debug(f"Conditional statement else: {else_stmts}")
            
        assert condition and then_stmts, "Conditional statement missing condition or statements"
        logger.debug(f"Conditional statement condition: {condition}, then statements: {then_stmts}, else statements: {else_stmts}")
        
        return Conditional(condition, then_stmts, else_stmts)
    
    def visitConditionalStatementElse(self, context: penguinParser.ConditionalStatementElseContext) -> List[ASTNode]:
        """Visit the else part of the conditional statement."""
        
        # Kan være det bare skal være del af conditional statement, da de bergge retuyreene conditional
        logger.info(f"Visiting conditional statement else: {context.getText()}")
        
        statements: List[ASTNode] = self.visit(context.statementBlock())

        assert statements, "Conditional statement else missing statements"
        logger.debug(f"Conditional statement else statements: {statements}")
        
        return statements
    
    def visitLoop(self, context: penguinParser.LoopContext) -> Loop:
        """Visits the loop context and creates a Loop AST node."""
        
        logger.info(f"Visiting loop: {context.getText()}")
        
        condition: ASTNode = self.visit(context.expression())
        statements: List[ASTNode] = self.visit(context.statementBlock())
        
        assert condition and statements, "Loop missing condition or statements"
        assert all(isinstance(stmt, ASTNode) for stmt in statements), "Not all statements are ASTNodes"
        logger.debug(f"Loop condition: {condition}, statements: {statements}")
        
        return Loop(condition, statements)
    
    def visitProcedureDeclaration(self, context: penguinParser.ProcedureDeclarationContext) -> ProcedureDef:
        """Visits the procedure declaration context and creates a ProcedureDef AST node."""
        
        logger.info(f"Visiting procedure declaration: {context.getText()}")
        
        # Retuern type can være helt tom
        return_type: str = context.type_().getText() if context.type_() else "void"
        name: str = context.IDENTIFIER().getText()
        
        assert return_type and name, "Procedure declaration missing return type or name"
        
        parametres: List[Tuple[str, str]] = []
        if context.parameterList():
            logger.debug("Procedure declaration has parameters")
            
            parametres_raw = self.visitParameterList(context.parameterList())
            assert parametres_raw, "Procedure declaration missing parameters"
            
            for i in range(len(parametres_raw)):
                logger.debug(f"Visiting parameter {i}: {parametres_raw[i].name}")
                
                parametre_type_: str = parametres_raw[i].var_type
                parametre_name: str = parametres_raw[i].name # IDENTIFIER fordi procedure calls can ikek have dot notation eller liste ting
                # TODO vær sikekr på at IDENTIFIER har getText()
                
                assert parametre_type_ and parametre_name, "Procedure declaration missing parameter type or name"
                
                parametres.append((parametre_type_, parametre_name))
            
            assert parametres, "Procedure declaration missing parameters"
            logger.debug(f"Procedure declaration parameters: {parametres}")
            
        statements: List[ASTNode] = self.visit(context.statementBlock())
        
        assert statements, "Procedure declaration missing statements"
        logger.debug(f"Procedure declaration return type: {return_type}, name: {name}, parameters: {parametres}, statements: {statements}")
        
        return ProcedureDef(return_type, name, parametres, statements)
    
    def visitReturnStatement(self, context: penguinParser.ReturnStatementContext) -> Return:
        """Visits the return statement context and creates a Return AST node."""
        
        logger.info(f"Visiting return statement: {context.getText()}")
        
        value = self.visit(context.expression())
        
        assert value, "Return statement missing value"
        logger.debug(f"Return statement value: {value}")
        
        return Return(value)
    
    def visitProcedureCallStatement(self, context: penguinParser.ProcedureCallStatementContext) -> ProcedureCallStatement:
        """Visit the procedure call statement context and creates a ProcedureCallStatement AST node."""
        
        logger.info(f"Visiting procedure call statement: {context.getText()}")
        
        call: ProcedureCall = self.visit(context.procedureCall())
        
        assert isinstance(call, ProcedureCall), "Procedure call statement missing procedure call"
        logger.debug(f"Procedure call statement: {call}")
        
        return ProcedureCallStatement(call)
    
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
        
        logger.info(f"Visiting expression: {context.getText()}")
        
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
        raise UnknownExpressionTypeError(f"Unknown expression type from {context.getText()}")
    
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
        logger.info(f"Visiting expr_val: {context.getText()}")
        
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
        raise UnknownValueTypeError(f"Unknown expr_val type from {context.getText()}") 
    
    def visitLiteral(self, context: penguinParser.LiteralContext) -> Union[IntegerLiteral, StringLiteral]:
        """Visits the literal context and creates an AST node (Finally).
        
        Forstil dig en verden af variabler, som alle er integers, og måske en streg
        Men henne gang kan det være skreven med hiroglyffer eller noget andet
        
        kig i visitLiteral classen i genereret antlr-py code for at finde ud af hvad der sker
        """
        logger.info(f"Visiting literal: {context.getText()}")
        
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
        raise UnknownLiteralTypeError(f"Unknown literal type from {context.getText()}")
    
    def visitName(self, context: penguinParser.NameContext) -> Union[AttributeAccess, Variable, ListAccess]:
        """Visits the name context and creates a Variable, AttributeAccess, or ListAccess AST node."""
        logger.info(f"Visiting name: {context.getText()}")
        assert context.IDENTIFIER(), "Name node has no identifiers"
        
        # Start with the base variable
        current_node = Variable(None, context.IDENTIFIER(0).getText())
        logger.debug(f"Base variable: {current_node}")
        
        # Parse the context to build up the access chain
        i = 1  # Start from the first token after the initial identifier
        
        # Count how many expressions we've processed
        expression_idx = 0
        identifier_idx = 1  # Skip the first identifier which was already processed
        
        while i < len(context.children):
            child = context.children[i]
            token_text = child.getText()
            
            if token_text == '.':
                # Attribute access: get the next identifier
                if identifier_idx < len(context.IDENTIFIER()):
                    attr_name = context.IDENTIFIER(identifier_idx).getText()
                    current_node = AttributeAccess(current_node, attr_name)
                    logger.debug(f"Created AttributeAccess: {current_node}")
                    identifier_idx += 1
                i += 2  # Skip the '.' and the identifier
            
            elif token_text == '[':
                # List access: collect all consecutive indices
                indices = []
                
                # Process this index
                if expression_idx < len(context.expression()):
                    index_expr = self.visit(context.expression(expression_idx))
                    indices.append(index_expr)
                    expression_idx += 1
                
                i += 3  # Skip '[', expression, and ']'
                
                # Look ahead for consecutive list accesses to flatten
                while i < len(context.children) and context.children[i].getText() == '[':
                    if expression_idx < len(context.expression()):
                        index_expr = self.visit(context.expression(expression_idx))
                        indices.append(index_expr)
                        expression_idx += 1
                    i += 3  # Skip '[', expression, and ']'
                
                # Create a single ListAccess with all the indices
                current_node = ListAccess(current_node, indices)
                logger.debug(f"Created ListAccess with indices: {current_node}")
            
            else:
                # Skip any other tokens
                i += 1
        
        return current_node
    
    def visitListAccess(self, context: penguinParser.ListAccessContext) -> ListAccess:
        """visit the list access context and creates a ListAccess AST node with flattened indices."""
        logger.info(f"Visiting list access: {context.getText()}")
        
        name = self.visit(context.name())
        current_indices: List[ASTNode] = self.visitExpressions(context.expressions())
        
        assert name and current_indices, "List access missing name or indices"
        
        if isinstance(name, ListAccess):
            base_name = name.name
            all_indices = name.indices + current_indices
            logger.debug(f"Flattened list access name: {base_name}, indices: {all_indices}")
            return ListAccess(base_name, all_indices)
        else:
            logger.debug(f"List access name: {name}, indices: {current_indices}")
            return ListAccess(name, current_indices)
    
    def visitAttributeAccess(self, context: penguinParser.AttributeAccessContext) -> AttributeAccess:
        """Visit the attribute access context and creates an AttributeAccess AST node."""
        
        logger.info(f"Visiting attribute access: {context.getText()}")
        
        name: ASTNode = self.visit(context.name())
        attribute: str = self.IDENTIFIER().getToken() # TODO tror der er fejl
        
        assert name and attribute, "Attribute access missing name or attribute"
        logger.debug(f"Attribute access name: {name}, attribute: {attribute}")
        
        return AttributeAccess(name, attribute)
    
    def visitProcedureCall(self, context: penguinParser.ProcedureCallContext) -> ProcedureCall:
        """Visit the procedure call context and creates a ProcedureCall AST node."""
        
        logger.info(f"Visiting procedure call: {context.getText()}")
        
        name: str = self.visit(context.name())
        
        assert name, "Procedure call missing name"
        
        # Ternary: hvis der er argumenter, så besøg dem og lav en liste af dem
        args: List[ASTNode] = self.visit(context.argumentList()) if context.argumentList() else []
        
        return ProcedureCall(name, args)
    
    """Visit Handlers
    
    En masse af det samme, men det ser pænere ud
    """
    
    def visitExpressions(self, context: penguinParser.ExpressionsContext) -> list[ASTNode]:
        """Handles the visit to multiple expressions in the CST."""
        
        logger.info(f"Visiting list of nodes: {context.getText()}")
        
        expressions: List[ASTNode] = [self.visit(expr) for expr in context.expression()]
        
        # isinstandce tjekker at et objekt X er af typen Y
        # all generere en liste af bolske værdier ud fra en for in generator
        assert all(isinstance(expr, ASTNode) for expr in expressions), "Not all expressions are ASTNodes"
        logger.debug(f"Visited expressions: {expressions}")
        
        return expressions
    
    def visitParameterList(self, context: penguinParser.ParameterListContext) -> List[Variable]:
        """Handles the visit to multiple parameters in the CST.
        
        Skal bruges til at generere AST'en for en procedure declaration
        """
        
        logger.info(f"Visiting parameter list: {context.getText()}")
        
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

        # assert that type and identifier are the same length
        assert len(context.type_()) == len(context.IDENTIFIER()), "Parameter list type and identifier length mismatch"
        
        # Zip de to lister sammen, så vi kan få fat i type og navn på samme tid
        for t, i in zip(context.type_(), context.IDENTIFIER()):
            # Besøg type og navn og lav en ny node Variable for hver parameter
            parametres.append(Variable(i.getText(), t.getText()))
        
        assert all(isinstance(param, ASTNode) for param in parametres), "Not all parameters are ASTNodes"
        logger.debug(f"Parameter list: {parametres}")
        
        return parametres # liste af en typle af to strenge
    
    def visitArgumentList(self, context: penguinParser.ArgumentListContext) -> List[ASTNode]:
        """Visits the argument list context and creates a list of AST nodes."""
        
        logger.info(f"Visiting argument list: {context.getText()}")
        
        # Arguments could could all come in some form of expression
        arguments: List[ASTNode] = [self.visitExpression(expression) for expression in context.expression()]
        
        assert all(isinstance(arg, ASTNode) for arg in arguments), "Not all arguments are ASTNodes" + "\n" + str(arguments)
        logger.debug(f"Argument list: {arguments}")
        
        return arguments
    
    def visitType(self, context: penguinParser.TypeContext) -> str:
        # ved ikk endnu om denen overhoved behøves at blvie implementeret
        # men den er der under visitor pattern koden
        logger.info(f"Visiting type: {context.getText()}")
        return super().visitType(context)
    
    def visitStatementBlock(self, context: penguinParser.StatementBlockContext) -> List[ASTNode]:
        """Visits a block of statements"""

        logger.info(f"Visiting statement block: {context.getText()}")
        
        statements: List[ASTNode] = [self.visit(statement) for statement in context.statement()]
        
        assert statements, "Statement block missing statements"
        assert all(isinstance(stmt, ASTNode) for stmt in statements), "Not all statements are ASTNodes" + "\n" + str(statements)
        logger.debug(f"Statement block: {statements}")
        
        return statements
