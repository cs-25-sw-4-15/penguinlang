"""_summary_
Types for the Penguin compiler.
"""

class Type:
    """_summary_
    Type base class for the Penguin compiler.
    """
    
    def __repr__(self):
        """
        Type representation.
        
        Returns:
            str: The name of the type.
        """
        
        return self.__class__.__name__
    
class IntType(Type):
    """_summary_
    Integer type.
    """
    
    pass

class StringType(Type):
    """_summary_
    String type.
    """
    
    pass

class ListType(Type):
    """_summary_
    List type.
    """
    
    #def __init__(self, element_type: Type):
        #"""
        #List type constructor.
        #
        #Args:
        #    element_type (Type): The type of the elements in the list.
        #"""
        
        #self.element_type = element_type
        
    def __repr__(self):
        """
        List type representation.
        
        Returns:
            str: The name of the type.
        """
        
        return f"List[{self.element_type}]"

# Singleton type instances for the Penguin compiler, used in the type checker and AST nodes.
INT = IntType()
STRING = StringType()
LIST = ListType()
