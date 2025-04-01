"""     
Abstract Syntaz tree node classes for the Penguin compiler.
"""

from types import INT, STRING, LIST

class ASTNode:
    """
    AST Base Class.
    
    Attributes:
        type (str): The type of the node.
        children (list[ASTNode]): The children of the node.
        value (Any): The value of the node.
    """
    
    def __init__(self, type, children=None, value=None):
        """_summary_
        AST Node Constructor

        Args:
            type (_type_): _description_
            children (_type_, optional): _description_. Defaults to None.
            value (_type_, optional): _description_. Defaults to None.
        """
        
        self.type = type
        self.children = children or []
        self.value = value

    def __repr__(self):
        """_summary_

        Returns:
            string: Printable representation of Node.
        """
        
        type_str = f": {self.type}" if self.type else ""
        if self.value:
            return f"{self.type}({self.value}){type_str}"
        
        return f"{self.type}({', '.join(map(str, self.children))}){type_str}"
    
class Integer(ASTNode):
    """
    Integer literal.
    """
    
    def __init__(self, value):
        super().__init__(INT, value=value)
        