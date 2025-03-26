# builds the Game Boy ROM from the source RGBASM code
rgbasm -o out.obj $1
rgblink -o $2 out.obj
rgbfix -v $2