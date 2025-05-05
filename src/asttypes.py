"""
Types for the Penguin compiler.
"""

# Typing modules
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    # Stops Pylance from complaining about the import. 
    # Recursive import, but only for type checking.
    from asttypes import IntType


class Type:
    """
    Type base class for the Penguin compiler.
    """
    
    def __eq__(self, other: Any) -> bool:
        """Check if two types are equal."""
        
        if not isinstance(other, Type):
            return False
        
        return type(self) == type(other)
    
    def __repr__(self) -> str:
        """Type representation.
        
        Returns:
            str: The name of the type.
        """
        classname = self.__class__.__name__
        fields = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{classname}({fields})"
    
    def is_indexable(self) -> bool:
        """Check if this type can be indexed (like arrays/lists).
        
        Returns:
            bool: True if this type can be indexed, False otherwise.
        """
        
        return False
    
    def index_result_type(self) -> None:
        """Get the type that results from indexing this type.
        Only relevant for indexable types.
        
        Returns:
            Type: The type of the indexed value, or None if not indexable.
        """
        
        return None

   
class VoidType(Type):
    """
    Void type.
    """
    
    def __init__(self) -> None:
        # Store class name in __class__ attribute
        self.__dict__["__class__"] = self.__class__.__name__
   
    def __repr__(self) -> str:
        """Void type representation.
        
        Returns:
            str: The name of the type.
        """
        return "void"


class TilesetType(Type):
    """
    Tileset type.
    """
    
    def __init__(self) -> None:
        # Store class name in __class__ attribute
        self.__dict__["__class__"] = self.__class__.__name__
    
    def is_indexable(self) -> bool:
        """Tilesets can be indexed."""
        
        return True
    
    def index_result_type(self) -> IntType:
        """Indexing a tileset returns an integer."""
        
        return IntType()
   
    def __repr__(self) -> str:
        """Tileset type representation.
        
        Returns:
            str: The name of the type.
        """
        
        return "tileset"


class TileMapType(Type):
    """
    TileMap type.
    """
    
    def __init__(self) -> None:
        # Store class name in __class__ attribute
        self.__dict__["__class__"] = self.__class__.__name__
    
    def is_indexable(self) -> bool:
        """TileMaps can be indexed."""
        
        return True
    
    def index_result_type(self) -> IntType:
        """Indexing a tilemap returns an integer."""
        
        return IntType()
   
    def __repr__(self) -> str:
        """
        TileMap type representation.
        
        Returns:
            str: The name of the type.
        """
        
        return "tilemap"


class SpriteType(Type):
    """
    Sprite type.
    """
    
    def __init__(self) -> None:
        # Store class name in __class__ attribute
        self.__dict__["__class__"] = self.__class__.__name__
   
    def __repr__(self) -> str:
        """Sprite type representation.
        
        Returns:
            str: The name of the type.
        """
        
        return "sprite"


class IntType(Type):
    """Integer type."""
    
    def __init__(self) -> None:
        # Store class name in __class__ attribute
        self.__dict__["__class__"] = self.__class__.__name__
   
    def __repr__(self) -> str:
        """Integer type representation.
        
        Returns:
            str: The name of the type.
        """
        
        return "int"


class StringType(Type):
    """String type."""
    
    def __init__(self) -> None:
        # Store class name in __class__ attribute
        self.__dict__["__class__"] = self.__class__.__name__
   
    def __repr__(self) -> str:
        """String type representation.
        
        Returns:
            str: The name of the type.
        """
        
        return "string"


class OAMEntryType(Type):
    """OAM Entry type - special type for sprite attributes in OAM.
    This allows accessing attributes like .x, .y, and .tile on OAM entries.
    """
    
    def __init__(self) -> None:
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
    
    def get_attribute_type(self, attr_name: str) -> Type:
        """Get the type of an attribute.
        
        Args:
            attr_name (str): The name of the attribute.
            
        Returns:
            Type: The type of the attribute, or None if the attribute is not valid.
        """
        
        return self.attributes.get(attr_name)
   
    def __repr__(self) -> str:
        """OAM Entry type representation.
        
        Returns:
            str: The name of the type.
        """
        
        return "oamentry"


class ListType(Type):
    """List type."""
   
    def __init__(self, element_type: Optional[Type] = None) -> None:
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
    
    def is_indexable(self) -> bool:
        """Lists can be indexed."""
        
        return True
    
    def index_result_type(self) -> Type:
        """Indexing a list returns its element type."""
        
        return self.element_type
    
    def __eq__(self, other: Any) -> bool:
        """Check if two list types are equal."""
        
        if not isinstance(other, ListType):
            return False
        
        return self.element_type == other.element_type
    
    def __repr__(self) -> str:
        """List type representation.
        
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
