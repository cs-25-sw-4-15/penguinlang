import os
import sys
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.astTypes import *


def initialize_hardware_elements() -> Tuple[Dict[str, Type], Dict[str, Tuple[List[Tuple[str, Type]], Type]]]:

    symbol_table: Dict[str, Type] = {}
    procedure_table: Dict[str, Tuple[List[Tuple[str, Type]], Type]] = {}
   
    symbol_table["display_tileset_block_0"] = TilesetType()  # Tileset that can be indexed
    symbol_table["display_tileset_block_1"] = TilesetType()  # Tileset that can be indexed
    symbol_table["display_tileset_block_2"] = TilesetType()  # Tileset that can be indexed
    symbol_table["display_tilemap0"] = TileMapType()  # TileMap that can be indexed

    symbol_table["display_oam_x"] = ListType(IntType())  # List of OAM entries
    symbol_table["display_oam_y"] = ListType(IntType())   # List of OAM entries
    symbol_table["display_oam_tile"] = ListType(IntType())   # List of OAM entries
    symbol_table["display_oam_attr"] = ListType(IntType())   # List of OAM entries
   
    # Control functions
    procedure_table["control_LCDon"] = ([], VoidType())
    procedure_table["control_LCDoff"] = ([], VoidType())
    procedure_table["control_waitVBlankStart"] = ([], VoidType())
    procedure_table["control_waitVBlankOver"] = ([], VoidType())
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
