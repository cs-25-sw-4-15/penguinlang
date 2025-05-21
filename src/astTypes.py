# Future imports (skal være først i filen)
from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, Any, Optional, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#Undgår cirkulære imports
if TYPE_CHECKING:
    from astTypes import IntType


class Type:
    
    def __eq__(self, other: Any) -> bool:
        
        return isinstance(other, Type)
    
    def __repr__(self) -> str:

        classname = self.__class__.__name__
        fields = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{classname}({fields})"
    
    def is_indexable(self) -> bool:

        return False
    
    def index_result_type(self) -> None:
        
        return None

   
class VoidType(Type):
    
    def __init__(self) -> None:
        self.__dict__["__class__"] = self.__class__.__name__
   
    def __repr__(self) -> str:

        return "void"


class TilesetType(Type):
    
    def __init__(self) -> None:
        self.__dict__["__class__"] = self.__class__.__name__
    
    def is_indexable(self) -> bool:
        
        return True
    
    def index_result_type(self) -> IntType:
        
        return IntType()
   
    def __repr__(self) -> str:
        
        return "tileset"


class TileMapType(Type):
    
    def __init__(self) -> None:

        self.__dict__["__class__"] = self.__class__.__name__
    
    def is_indexable(self) -> bool:
        
        return True
    
    def index_result_type(self) -> IntType:
        
        return IntType()
   
    def __repr__(self) -> str:
        
        return "tilemap"


class SpriteType(Type):
    
    def __init__(self) -> None:

        self.__dict__["__class__"] = self.__class__.__name__
   
    def __repr__(self) -> str:
        
        return "sprite"


class IntType(Type):
    
    def __init__(self) -> None:

        self.__dict__["__class__"] = self.__class__.__name__
   
    def __repr__(self) -> str:
        
        return "int"


class StringType(Type):
    
    def __init__(self) -> None:

        self.__dict__["__class__"] = self.__class__.__name__
   
    def __repr__(self) -> str:
        
        return "string"

# Deprecated, remaining uses still exist in type checker and tests
# TODO Remove said uses
class OAMEntryType(Type):
    
    def __init__(self) -> None:
        
        self.__dict__["__class__"] = self.__class__.__name__
        
        self.attributes = {
            "x": IntType(),
            "y": IntType(),
            "tile": IntType()
        }
    
    def get_attribute_type(self, attr_name: str) -> Type:
        
        return self.attributes.get(attr_name)
   
    def __repr__(self) -> str:
        
        return "oamentry"


class ListType(Type):
   
    def __init__(self, element_type: Optional[Type] = None) -> None:

        self.__dict__["__class__"] = self.__class__.__name__
        
        self.element_type = element_type if element_type is not None else IntType()
    
    def is_indexable(self) -> bool:

        return True
    
    def index_result_type(self) -> Type:
        
        return self.element_type
    
    def __eq__(self, other: Any) -> bool:
        
        if not isinstance(other, ListType):
            return False
        
        return self.element_type == other.element_type
    
    def __repr__(self) -> str:
        
        return f"List[{self.element_type}]"


class ProcedureType:
    def __init__(self, param_types: List[Type], return_type: Type):
        self.param_types = param_types
        self.return_type = return_type

    def __repr__(self):
        return f"Procedure(param_types={self.param_types}, return_type={self.return_type})"


# Singleton type instances used in the type checker and AST nodes.
INT = IntType()
STRING = StringType()
VOID = VoidType()
TILESET = TilesetType()
TILEMAP = TileMapType()
SPRITE = SpriteType()
#Deprecated af
OAM_ENTRY = OAMEntryType()
