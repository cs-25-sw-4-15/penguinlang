"""
Predefined hardware registers and functions for the Penguin language.
This file defines built-in hardware elements that are available to all programs.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Dict, List, Tuple

# Import the type classes from the main type checker
from src.astTypes import *


def initialize_hardware_elements() -> Tuple[Dict[str, Type], Dict[str, Tuple[List[Tuple[str, Type]], Type]]]:
    """
    Initialize all predefined hardware modules, registers, and functions.
   
    Returns:
        Tuple containing:
        - Dictionary mapping variable names to their types
        - Dictionary mapping procedure names to (param_types, return_type)
    """
    symbol_table: Dict[str, Type] = {}
    procedure_table: Dict[str, Tuple[List[Tuple[str, Type]], Type]] = {}
   
    # Display subsystems - these are special hardware elements
    # They are of their specific type, but can be indexed like arrays
    symbol_table["display_tileset0"] = TilesetType()  # Tileset that can be indexed
    symbol_table["display_tilemap0"] = TileMapType()  # TileMap that can be indexed
    
    # OAM (Object Attribute Memory) is a special list that contains sprite attributes
    symbol_table["display_oam_x"] = ListType(IntType())  # List of OAM entries
    symbol_table["display_oam_y"] = ListType(IntType())   # List of OAM entries
    symbol_table["display_oam_tile"] = ListType(IntType())   # List of OAM entries
    symbol_table["display_oam_attr"] = ListType(IntType())   # List of OAM entries
   
    # Control functions
    procedure_table["control_LCDon"] = ([], VoidType())
    procedure_table["control_LCDoff"] = ([], VoidType())
    procedure_table["control_waitVBlank"] = ([], VoidType())
    procedure_table["control_updateInput"] = ([], VoidType())
   
    # Input flags - these are boolean values represented as integers
    symbol_table["input_Right"] = IntType()
    symbol_table["input_Left"] = IntType()
    symbol_table["input_Up"] = IntType()
    symbol_table["input_Down"] = IntType()
    symbol_table["input_A"] = IntType()
    symbol_table["input_B"] = IntType()
    symbol_table["input_Start"] = IntType()
    symbol_table["input_Select"] = IntType()
   
    return symbol_table, procedure_table
