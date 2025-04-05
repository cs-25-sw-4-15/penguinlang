"""Abstract Syntaz tree node classes for the Penguin compiler."""

from typing import Any


class ASTNode:
    """AST Base Class.
    
    Attributes:
        type (str): The type of the node.
        children (list[ASTNode]): The children of the node.
        value (Any): The value of the node.
    """
    
    def __init__(self, type, children=None, value=None):
        """AST Node Constructor"""
        
        self.type = type
        self.children = children or []
        self.value = value

    def __repr__(self):
        """___repr__ method

        Returns:
            string: Printable representation of Node.
        """
        
        type_str = f": {self.type}" if self.type else ""
        if self.value:
            return f"{self.type}({self.value}){type_str}"
        
        return f"{self.type}({', '.join(map(str, self.children))}){type_str}"


"""Note to self

Order og classes: 
- program
    - Program
- statements
    - Declaration, Assignment, Initialization, ListInitialization
    - If, While, Return, ProcedureCall, ProcedureCallStatement
- expressions
    - BinaryOp, UnaryOp
    - Variable, Number, String
    - ListAccess, AttributeAccess
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
    
    Args:
        ASTNode (none): Base class for all AST nodes.
        
    Attributes:
        value (Any): The value of the node.
    """
    
    def __init__(self, value):
        super().__init__(None, value=value)


class Program(ASTNode):
    """Progam AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
    
    Attributes:
        statements (list[ASTNode]): The statements in the program.
    """
    
    def __init__(self, statements: list[ASTNode]):
        self.statements = statements
        

class Declaration(ASTNode):
    """Declaration Statement AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
    
    Attributes:
        var_type (Type): The type of the variable.
        name (str): The name of the variable.
    """
    
    def __init__(self, var_type, name: str): 
        # TODO: mangler type var_type, det kan være mange, så måske "Any"?
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
    
    def __init__(self, target: str, value: Any):
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
    
    def __init__(self, var_type, name: str, value: Any):
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
    
    def __init__(self, name: str, values): 
        # TODO: type for values, det er nok en liste af INT type
        self.name = name
        self.values = values


class If(ASTNode):
    """If Statement AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
    
    Attributes:
        condition (Any): The condition to evaluate the if statement.
        body (list[ASTNode]): The statements to execute if the condition is true.
        else_body (list[ASTNode]): Default: None. The statements to execute if the condition is false. 
    """
    
    def __init__(self, condition: Any, then_body: list[ASTNode], else_body: list[ASTNode] = None):
        self.condition = condition
        self.then_body = then_body # Liste of statements
        self.else_body = else_body # Liste of statements


class Loop(ASTNode):
    """Loop Statement AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
    
    Attributes:
        condition (Any): The condition to evaluate the loop statement.
        body (list[ASTNode]): The statements to execute if the condition is true.
    """
    
    def __init__(self, condition: Any, body: list[ASTNode]):
        self.condition = condition
        self.body = body # Liste of statements
        
        
class Return(ASTNode):
    """Return Statement AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
    
    Attributes:
        value (Any): The value to return from the function. (Sematically should only be integers)
    """
    
    def __init__(self, value: Any): 
        # TODO: evaluer om type skal være INT i stedet for Any
        self.value = value 


class ProcedureCallStatement(ASTNode):
    """Procedure Call Statement AST Node.
    
    Attributes:
    Call (str): The name of the procedure to call.
    """
    
    def __init__(self, call: str):
        self.call = call


class BinaryOp(ASTNode):
    """hii

    Args:
        ASTNode (none): Base class for all AST nodes.
        
    Attributes:
        left (Any): The left operand of the binary operation.
        op (str): The operator of the binary operation.
        right (Any): The right operand of the binary operation.
    """
    
    def __init__(self, left: Any, op: str, right: Any):
        self.left = left
        self.op = op
        self.right = right


class UnaryOp(ASTNode):
    """Unary Operation AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
        
    Attributes:
        op (str): The operator of the unary operation.
        operand (Any): The operand of the unary operation.
    """
    
    def __init__(self, op: str, operand: Any):
        self.op = op
        self.operand = operand


class IntegerLiteral(ASTNode):
    """Integer Literal AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
        
    Attributes:
        value (int): The value of the integer.
    """
    
    def __init__(self, value: int):
        self.value = value
        

class StringLiteral(ASTNode):
    """String Literal AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
        
    Attributes:
        value (str): The value of the string.
    """
    
    def __init__(self, value: str):
        self.value = value
        

class Variable(ASTNode):
    """Variable AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
        
    Attributes:
        name (str): The name of the variable.
    """
    
    def __init__(self, name: str):
        self.name = name
        

class ListAccess(ASTNode):
    """List Access AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
        
    Attributes:
        name (str): The name of the list.
        index (int): The index of the element in the list.
    """
    
    def __init__(self, name: str, indices: int):
        self.name = name
        self.indices = indices # En liste af expressions


class AttributeAccess(ASTNode):
    """Attribute Access AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
        
    Attributes:
        name (str): The name of the attribute.
        attribute (str): The name of the attribute to access.
    """
    
    def __init__(self, name: str, attribute: str):
        self.name = name
        self.attribute = attribute 
        

class ProcesureCall(ASTNode):
    """Procedure Call AST Node.
    
    Args:
        ASTNode (none): Base class for all AST nodes.
        
    Attributes:
        name (str): The name of the procedure to call.
        args (list[ASTNode]): The arguments to pass to the procedure.
    """
    
    def __init__(self, name: str, args: list[ASTNode]):
        self.name = name
        self.args = args


class ProcedureDef(ASTNode):
    """Procedure Definition AST Node
    
    Args:
        ASTNode (none): Base class for all AST nodes.
    
    Attributes:
        name (str): The name of the procedure.
        params (list[ASTNode]): The parameters of the procedure.
        body (list[ASTNode]): The body of the procedure.
    """
    
    def __init__(self, return_type, name: str, params: list[ASTNode], body: list[ASTNode]): 
        # TODO: type for return_type
        self.return_type = return_type 
        self.name = name
        self.params = params
        self.body = body
