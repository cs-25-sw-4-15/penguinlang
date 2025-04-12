"""
Types for the Penguin compiler.
"""
class Type:
    """
    Type base class for the Penguin compiler.
    """
    
    def __eq__(self, other):
        """Check if two types are equal."""
        if not isinstance(other, Type):
            return False
        return type(self) == type(other)
    
    def __repr__(self):
        """
        Type representation.
        
        Returns:
            str: The name of the type.
        """
        classname = self.__class__.__name__
        fields = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{classname}({fields})"
    
    def is_indexable(self):
        """
        Check if this type can be indexed (like arrays/lists).
        
        Returns:
            bool: True if this type can be indexed, False otherwise.
        """
        return False
    
    def index_result_type(self):
        """
        Get the type that results from indexing this type.
        Only relevant for indexable types.
        
        Returns:
            Type: The type of the indexed value, or None if not indexable.
        """
        return None
   
class VoidType(Type):
    """
    Void type.
    """
    
    def __init__(self):
        # Store class name in __class__ attribute
        self.__dict__["__class__"] = self.__class__.__name__
   
    def __repr__(self):
        """
        Void type representation.
        
        Returns:
            str: The name of the type.
        """
        return "void"
   
class TilesetType(Type):
    """
    Tileset type.
    """
    
    def __init__(self):
        # Store class name in __class__ attribute
        self.__dict__["__class__"] = self.__class__.__name__
    
    def is_indexable(self):
        """Tilesets can be indexed."""
        return True
    
    def index_result_type(self):
        """Indexing a tileset returns an integer."""
        return IntType()
   
    def __repr__(self):
        """
        Tileset type representation.
        
        Returns:
            str: The name of the type.
        """
        return "Tileset"
   
class TileMapType(Type):
    """
    TileMap type.
    """
    
    def __init__(self):
        # Store class name in __class__ attribute
        self.__dict__["__class__"] = self.__class__.__name__
    
    def is_indexable(self):
        """TileMaps can be indexed."""
        return True
    
    def index_result_type(self):
        """Indexing a tilemap returns an integer."""
        return IntType()
   
    def __repr__(self):
        """
        TileMap type representation.
        
        Returns:
            str: The name of the type.
        """
        return "TileMap"
   
class SpriteType(Type):
    """
    Sprite type.
    """
    
    def __init__(self):
        # Store class name in __class__ attribute
        self.__dict__["__class__"] = self.__class__.__name__
   
    def __repr__(self):
        """
        Sprite type representation.
        
        Returns:
            str: The name of the type.
        """
        return "Sprite"
   
class IntType(Type):
    """
    Integer type.
    """
    
    def __init__(self):
        # Store class name in __class__ attribute
        self.__dict__["__class__"] = self.__class__.__name__
   
    def __repr__(self):
        """
        Integer type representation.
        
        Returns:
            str: The name of the type.
        """
        return "int"

class StringType(Type):
    """
    String type.
    """
    
    def __init__(self):
        # Store class name in __class__ attribute
        self.__dict__["__class__"] = self.__class__.__name__
   
    def __repr__(self):
        """
        String type representation.
        
        Returns:
            str: The name of the type.
        """
        return "String"

class OAMEntryType(Type):
    """
    OAM Entry type - special type for sprite attributes in OAM.
    This allows accessing attributes like .x, .y, and .tile on OAM entries.
    """
    
    def __init__(self):
        """
        Initialize OAM entry type with its valid attributes.
        """
        # Store class name in __class__ attribute
        self.__dict__["__class__"] = self.__class__.__name__
        
        # Dictionary of valid attributes and their types
        self.attributes = {
            "x": IntType(),
            "y": IntType(),
            "tile": IntType()
        }
    
    def get_attribute_type(self, attr_name):
        """
        Get the type of an attribute.
        
        Args:
            attr_name (str): The name of the attribute.
            
        Returns:
            Type: The type of the attribute, or None if the attribute is not valid.
        """
        return self.attributes.get(attr_name)
   
    def __repr__(self):
        """
        OAM Entry type representation.
        
        Returns:
            str: The name of the type.
        """
        return "OAMEntry"

class ListType(Type):
    """
    List type.
    """
   
    def __init__(self, element_type=None):
        """
        List type constructor.
        
        Args:
            element_type (Type, optional): The type of the elements in the list.
                For user-defined lists, this will always be IntType.
                For predefined lists, this can be any type specified.
        """
        # Store class name in __class__ attribute
        self.__dict__["__class__"] = self.__class__.__name__
        
        self.element_type = element_type if element_type is not None else IntType()
    
    def is_indexable(self):
        """Lists can be indexed."""
        return True
    
    def index_result_type(self):
        """Indexing a list returns its element type."""
        return self.element_type
    
    def __eq__(self, other):
        """Check if two list types are equal."""
        if not isinstance(other, ListType):
            return False
        return self.element_type == other.element_type
    
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
VOID = VoidType()
TILESET = TilesetType()
TILEMAP = TileMapType()
SPRITE = SpriteType()
OAM_ENTRY = OAMEntryType()