def codegenRegister() -> dict[str,str]:
    dict_to_return = {}
    dict_to_return['display_tileset0'] = "$9000"
    dict_to_return["display_tilemap0"] = "$9800"
    
    dict_to_return["display_oam_x"] = ""
    dict_to_return["display_oam_y"] =  "" 
    dict_to_return["display_oam_tile"] = ""   
    return dict_to_return 