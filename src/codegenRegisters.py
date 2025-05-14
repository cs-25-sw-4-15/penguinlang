""" Register file for the Penguin compiler

This file contains memory addresses for the hardware registers
"""


def codegenRegister() -> dict[str,str]:
    dict_to_return = {}
    dict_to_return['display_tileset_block_0'] = "$8000"
    dict_to_return['display_tileset_block_1'] = "$8800"
    dict_to_return['display_tileset_block_2'] = "$9000"
    dict_to_return["display_tilemap0"] = "$9800"
    
    dict_to_return["display_oam_x"] = str(0xFE00 + 1)
    dict_to_return["display_oam_y"] = str(0xFE00)
    dict_to_return["display_oam_tile"] = str(0xFE00 + 2)
    dict_to_return["display_oam_attr"] = str(0xFE00 + 3)
    
    return dict_to_return
