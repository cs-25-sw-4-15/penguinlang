"""Prdefines Functions and Variables for the Penguin Language

Predefined hardware registers and functions for the Penguin language.
This file defines built-in hardware elements that are available to all programs.
"""

# Stdlib imports
import os
import sys
from typing import Dict, List, Tuple

# Extend module paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Custom modules
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
    symbol_table["display_tileset_block_0"] = TilesetType()  # Tileset that can be indexed
    symbol_table["display_tileset_block_1"] = TilesetType()  # Tileset that can be indexed
    symbol_table["display_tileset_block_2"] = TilesetType()  # Tileset that can be indexed
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
    procedure_table["control_initPalette"] = ([], VoidType())
    procedure_table["control_initDisplayRegs"] = ([], VoidType())
    procedure_table["control_checkLeft"] = ([], IntType())
    procedure_table["control_checkRight"] = ([], IntType())
    procedure_table["control_checkUp"] = ([], IntType())
    procedure_table["control_checkDown"] = ([], IntType())
    procedure_table["control_checkA"] = ([], IntType())
    procedure_table["control_checkB"] = ([], IntType())
    procedure_table["control_checkStart"] = ([], IntType())
    procedure_table["control_checkSelect"] = ([], IntType())
   
    return symbol_table, procedure_table
