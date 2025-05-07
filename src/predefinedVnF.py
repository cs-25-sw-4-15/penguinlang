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
    symbol_table["display.tileset0"] = TilesetType()  # Tileset that can be indexed
    symbol_table["display.tilemap0"] = TileMapType()  # TileMap that can be indexed
    
    # OAM (Object Attribute Memory) is a special list that contains sprite attributes
    symbol_table["display.oam"] = ListType(OAMEntryType())  # List of OAM entries
   
    # Control functions
    procedure_table["control.LCDon"] = ([], VoidType())
    procedure_table["control.LCDoff"] = ([], VoidType())
    procedure_table["control.waitVBlank"] = ([], VoidType())
    procedure_table["control.updateInput"] = ([], VoidType())
   
    # Input flags - these are boolean values represented as integers
    symbol_table["input.Right"] = IntType()
    symbol_table["input.Left"] = IntType()
    symbol_table["input.Up"] = IntType()
    symbol_table["input.Down"] = IntType()
    symbol_table["input.A"] = IntType()
    symbol_table["input.B"] = IntType()
    symbol_table["input.Start"] = IntType()
    symbol_table["input.Select"] = IntType()
   
    return symbol_table, procedure_table
