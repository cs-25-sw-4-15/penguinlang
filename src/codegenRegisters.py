def codegenRegister() -> dict[str,str]:
    dict_to_return = {}
    dict_to_return['display_tileset0'] = "$9000"
    dict_to_return["display_tilemap0"] = "$9800"
    
    dict_to_return["display_oam_x"] = str(0xFE00 + 1)
    dict_to_return["display_oam_y"] =  str(0xFE00)
    dict_to_return["display_oam_tile"] = str(0xFE00 + 2)
    dict_to_return["display_oam_attr"] = str(0xFE00 + 3)
    return dict_to_return 