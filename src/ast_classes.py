"""Abstract Syntaz tree node classes for the Penguin compiler.

Defining the AST node classes for the Penguin compiler.
"""


# Typing modules
from __future__ import annotations # PEP 563 style. For forward references, e.g. ProcedureCall
from typing import Optional, Union, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    # Stops Pylance from complaining about the import. 
    # Recursive import, but only for type checking.
    from ast import ProcedureCall


class ASTNode:
    """AST Base Class.
    
    Attributes:
        type (str): The type of the node.
        children (list[ASTNode]): The children of the node.
        value (Any): The value of the node.
    
    Update:
        Constructor does not get used by any class idealy.
        The constructor is used for the base class ASTNode.
    """
    
    def __init__(self, type, children=None, value=None) -> None:
        """AST Node Constructor"""
        
        self.type = type
        self.children = children or []
        self.value = value

    def __repr__(self) -> str:
        """___repr__ method

        Returns:
            string: Printable representation of Node.
        """
        
        classname = self.__class__.__name__
        fields = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{classname}({fields})"


"""Note to self

Order og classes: 
- program:
    - Program
- statements
    - Declaration
    - Assignment
    - Initialization
    - ListInitialization
    - If
    - Loop
    - Return
    - ProcedureCallStatement
- expressions:
    - BinaryOp
    - UnaryOp
    - IntegerLiteral
    - StringLiteral
    - Variable
    - ListAccess
    - AttributeAccess
- procedures
    - ProcedureDef

Grammar that dose not need to be implemented as they are helper-grammar
- name
- expressions
- parametrelist
- argumentlist
"""


class example(ASTNode):
    """Example AST Node.
    
    SKAL ALDRIG KALDES
    NEVER VISIT/CALL THIS CLASS
    
    Args:
        ASTNode (none): Base class for all AST nodes.
        
    Attributes:
        value (Any): The value of the node.
    """
    
    def __init__(self, value: ASTNode) -> None:
        super().__init__(None, value=value)


"""Program"""


class Program(ASTNode):
    """Progam AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
    
    Attributes:
        statements (list[ASTNode]): The statements in the program.
    """
    
    def __init__(self, statements: List[ASTNode]) -> None:
        self.statements = statements
        

"""Statements"""


class Declaration(ASTNode):
    """Declaration Statement AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
    
    Attributes:
        var_type (Type): The type of the variable.
        name (str): The name of the variable.
    """
    
    def __init__(self, var_type: str, name: str) -> None: 
        self.var_type = var_type
        self.name = name


class Assignment(ASTNode):
    """Assignment Statement AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
    
    Attributes:
        target (str): The target variable to assign to. (Varaible, ListAccess, AttributeAccess)
        value (Any): The value to assign to the target. (Variable, Number, String, ListAccess, AttributeAccess)
    """
    
    def __init__(self, target: ASTNode, value: ASTNode) -> None:
        self.target = target
        self.value = value


class Initialization(ASTNode):
    """Initialization Statement AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
    
    Attributes:
        var_type (Type): The type of the variable.
        name (str): The name of the variable.
        value (Any): The value to assign to the target. (Variable, Number, String, ListAccess, AttributeAccess)
    """
    
    def __init__(self, var_type: str, name: str, value: ASTNode) -> None:
        self.var_type = var_type
        self.name = name
        self.value = value


class ListInitialization(ASTNode):
    """List Initialization Statement AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
    
    Attributes:
        name (str): The name of the variable.
        value (Any): The value to assign to the target. (Variable, Number, String, ListAccess, AttributeAccess)
    """
    
    def __init__(self, name: str, values: List[ASTNode]) -> None: 
        self.name = name
        self.values = values


class Conditional(ASTNode):
    """If Statement AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
    
    Attributes:
        condition (Any): The condition to evaluate the if statement.
        body (list[ASTNode]): The statements to execute if the condition is true.
        else_body (list[ASTNode]): Default: None. The statements to execute if the condition is false. 
    """
    
    def __init__(self, condition: ASTNode, then_body: List[ASTNode], else_body: Optional[List[ASTNode]] = None) -> None:
        self.condition = condition
        self.then_body = then_body # Liste of statements
        self.else_body = else_body or [] # Liste of statements, men kan være tom


class Loop(ASTNode):
    """Loop Statement AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
    
    Attributes:
        condition (Any): The condition to evaluate the loop statement.
        body (list[ASTNode]): The statements to execute if the condition is true.
    """
    
    def __init__(self, condition: ASTNode, body: List[ASTNode]) -> None:
        self.condition = condition
        self.body = body # Liste of statements
        
        
class Return(ASTNode):
    """Return Statement AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
    
    Attributes:
        value (Any): The value to return from the function. (Sematically should only be integers)
    """
    
    def __init__(self, value: ASTNode) -> None: 
        self.value = value 


class ProcedureCallStatement(ASTNode):
    """Procedure Call Statement AST Node.
    
    Attributes:
    Call (str): The name of the procedure to call.
    """
    
    def __init__(self, call: "ProcedureCall") -> None: # noqa: ProcedureCall
        # ProcedureCall er en klasse, der repræsenterer et procedurekald
        # Den indeholder navnet på proceduren og argumenterne
        # som en liste af AST-noder
        # call er en instans af ProcedureCall-klassen
        self.call = call


"""Expressions"""


class BinaryOp(ASTNode):
    """Binary Operation Expression AST Node.

    Args:
        ASTNode (none): Base class for all AST nodes.
        
    Attributes:
        left (ASTNode): The left operand of the binary operation.
        op (str): The operator of the binary operation.
        right (ASTNode): The right operand of the binary operation.
    """
    
    def __init__(self, left: ASTNode, op: str, right: ASTNode) -> None:
        self.left = left
        self.op = op
        self.right = right


class UnaryOp(ASTNode):
    """Unary Operation Expression AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
        
    Attributes:
        op (str): The operator of the unary operation.
        operand (ASTNode): The operand of the unary operation.
    """
    
    def __init__(self, op: str, operand: ASTNode) -> None:
        self.op = op
        self.operand = operand


class IntegerLiteral(ASTNode):
    """Integer Literal Expression AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
        
    Attributes:
        value (str): The value of the integer.
    """
    
    def __init__(self, value: Union[int, str]) -> None:
        # value kan være int eller str, da det kan være en hex- eller binærværdi
        # burde enlig bare være str, men det er lidt mere "pænt" at have det som int
        self.value = value
        

class StringLiteral(ASTNode):
    """String Literal Expression AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
        
    Attributes:
        value (str): The value of the string.
    """
    
    def __init__(self, value: str) -> None:
        # value kan være str, da det er det det er
        self.value = value
        

class Variable(ASTNode):
    """Variable Expression AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
        
    Attributes:
        name (str): The name of the variable.
    """
    
    def __init__(self, name: str) -> None:
        self.name = name
        

class ListAccess(ASTNode):
    """List Access Expression AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
        
    Attributes:
        name (str): The name of the list.
        index (int): The index of the element in the list.
    """
    
    def __init__(self, name: str, indices: List[ASTNode]) -> None:
        self.name = name
        self.indices = indices # En liste af expressions, som repræsenterer indekserne


class AttributeAccess(ASTNode):
    """Attribute Access Expression AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
        
    Attributes:
        name (str): The name of the attribute.
        attribute (str): The name of the attribute to access.
    """
    
    def __init__(self, name: str, attribute: str) -> None:
        self.name = name
        self.attribute = attribute 
        

class ProcedureCall(ASTNode):
    """Procedure Call Expression AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
        
    Attributes:
        name (str): The name of the procedure to call.
        args (list[ASTNode]): The arguments to pass to the procedure.
    """
    
    def __init__(self, name: str, args: List[ASTNode]) -> None:
        self.name = name
        self.args = args


"""Procedures"""


class ProcedureDef(ASTNode):
    """Procedure Definition AST Node
    
    Args:
        ASTNode (none): Base class for all AST nodes.
    
    Attributes:
        name (str): The name of the procedure.
        params (list[ASTNode]): The parameters of the procedure.
        body (list[ASTNode]): The body of the procedure.
    """
    
    def __init__(self, return_type: Optional[str], name: str, 
                 params: List[Tuple[str, str]], body: List[ASTNode]) -> None: 
        # Optional[str] for return_type, da det kan være None
        # List[Tuple[str, str]] for params, da det er en liste af tuples med (type, name)
        self.return_type = return_type 
        self.name = name
        self.params = params
        self.body = body
