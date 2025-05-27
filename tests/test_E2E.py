import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import glob
from pyboy import PyBoy
from src.compiler import full_compile

data_segment_start = 0xC010
program_start = 0x0150


def nop_reached(pyboy):
    return pyboy.memory[pyboy.register_file.PC] == 0x00


def compile_source_to_binary(source_code: str, output_dir: str = 'temp_files') -> str:
    os.makedirs(output_dir, exist_ok=True)
    source_file_path = os.path.join(output_dir, 'temp_source.peg')
    binary_file_path = os.path.join(output_dir, 'temp_binary.gb')

    test_files_dir = os.path.join(os.path.dirname(__file__), 'test_files')
    for file in glob.glob(os.path.join(test_files_dir, '*')):
        if os.path.isfile(file):
            dest_file = os.path.join(output_dir, os.path.basename(file))
            if not os.path.exists(dest_file):
                with open(file, 'rb') as src_file:
                    with open(dest_file, 'wb') as dst_file:
                        dst_file.write(src_file.read())

    with open(source_file_path, 'w') as source_file:
        source_file.write(source_code)

    full_compile(source_file_path, output_file=binary_file_path, p=True)

    return binary_file_path


def teardown():
    temp_files_dir = 'temp_files'
    if os.path.exists(temp_files_dir):
        for file in glob.glob(os.path.join(temp_files_dir, '*')):
            try:
                os.remove(file)
            except Exception as e:
                print(f"Error deleting file {file}: {e}")
    else:
        os.makedirs(temp_files_dir)


def test_addition_1():
    """
    End-to-end test for simple addition operation.
    """
    source_code = """
    int Result1 = 2 + 3;
    int Result2 = 5 + 7;
    int Result3 = 10 + 20;
    int Result4 = 0 + 2;
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result1 = pyboy.memory[data_segment_start]
    result2 = pyboy.memory[data_segment_start + 1]
    result3 = pyboy.memory[data_segment_start + 2]
    result4 = pyboy.memory[data_segment_start + 3]

    pyboy.stop()

    assert result1 == 5
    assert result2 == 12
    assert result3 == 30
    assert result4 == 2

    teardown()


def test_subtraction_1():
    """
    End-to-end test for simple subtraction operation.
    """
    source_code = """
    int Result1 = 5 - 3;
    int Result2 = 10 - 7;
    int Result3 = 20 - 10;
    int Result4 = 0 - 2;
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result1 = pyboy.memory[data_segment_start]
    result2 = pyboy.memory[data_segment_start + 1]
    result3 = pyboy.memory[data_segment_start + 2]
    result4 = pyboy.memory[data_segment_start + 3]

    pyboy.stop()

    assert result1 == 2
    assert result2 == 3
    assert result3 == 10
    assert result4 == 254

    teardown()


def test_multiplication_1(): # four subresults
    """
    End-to-end test for simple multiplication operation.
    """
    source_code = """
    int Result1 = 2 * 3;
    int Result2 = 5 * 7;
    int Result3 = 10 * 20;
    int Result4 = 0 * 2;
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result1 = pyboy.memory[data_segment_start]
    result2 = pyboy.memory[data_segment_start + 1]
    result3 = pyboy.memory[data_segment_start + 2]
    result4 = pyboy.memory[data_segment_start + 3]

    pyboy.stop()

    assert result1 == 6
    assert result2 == 35
    assert result3 == 200
    assert result4 == 0

    teardown()


def test_multiplication_2():
    """
    End-to-end test for a multiplication operation with overflow.
    """
    source_code = """
    int Result = 0;
    int Integer1 = 255;

    int Integer2 = 255;

    Result = Integer1 * Integer2;
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]
    pyboy.stop()

    assert result == 1

    teardown()


def test_function_call_1():
    """
    End-to-end test for a function call.
    """
    source_code = """
    procedure int Add(int a, int b) {
        return a + b;
    }

    int Result = 0;

    Result = Add(10, 20);
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]
    pyboy.stop()

    assert result == 30

    teardown()


def test_if_else_branch():
    """
    End-to-end test for if-else branching.
    """
    source_code = """
    int Result = 0;
    int Condition = 1;

    if (Condition == 1) {
        Result = 10;
    } else {
        Result = 20;
    }
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]
    pyboy.stop()

    assert result == 10

    teardown()


def test_equality_and_inequality():
    """
    End-to-end test for equality (==) and inequality (!=) operators.
    """
    source_code = """
    int Result1 = 12 != 13;
    int Result2 = 12 == 13;
    int Result3 = 12 == 12;
    int Result4 = 12 != 12;
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result1 = pyboy.memory[data_segment_start]
    result2 = pyboy.memory[data_segment_start + 1]
    result3 = pyboy.memory[data_segment_start + 2]
    result4 = pyboy.memory[data_segment_start + 3]

    pyboy.stop()

    assert result1 == 1
    assert result2 == 0
    assert result3 == 1
    assert result4 == 0
    teardown()


def test_comparisons():
    """
    End-to-end test for comparison operators (<, >, <=, >=).
    """
    source_code = """
    int Result1 = 5 < 10;
    int Result2 = 10 > 5;
    int Result3 = 5 <= 5;
    int Result4 = 5 >= 10;
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result1 = pyboy.memory[data_segment_start]
    result2 = pyboy.memory[data_segment_start + 1]
    result3 = pyboy.memory[data_segment_start + 2]
    result4 = pyboy.memory[data_segment_start + 3]

    pyboy.stop()

    assert result1 == 1
    assert result2 == 1
    assert result3 == 1
    assert result4 == 0

    teardown()


def test_logical_and():
    """
    End-to-end test for logial and
    """
    source_code = """
    int Result1 = 1 and 1;
    int Result2 = 1 and 0;
    int Result3 = 0 and 1;
    int Result4 = 0 and 0;
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result1 = pyboy.memory[data_segment_start]
    result2 = pyboy.memory[data_segment_start + 1]
    result3 = pyboy.memory[data_segment_start + 2]
    result4 = pyboy.memory[data_segment_start + 3]

    pyboy.stop()

    assert result1 == 1
    assert result2 == 0
    assert result3 == 0
    assert result4 == 0

    teardown()


def test_logical_or():
    """
    End-to-end test for logial or
    """
    source_code = """
    int Result1 = 1 or 1;
    int Result2 = 1 or 0;
    int Result3 = 0 or 1;
    int Result4 = 0 or 0;
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result1 = pyboy.memory[data_segment_start]
    result2 = pyboy.memory[data_segment_start + 1]
    result3 = pyboy.memory[data_segment_start + 2]
    result4 = pyboy.memory[data_segment_start + 3]

    pyboy.stop()

    assert result1 == 1
    assert result2 == 1
    assert result3 == 1
    assert result4 == 0

    teardown()


def test_bitwise_and():
    """
    End-to-end test for bitwise and operator (&).
    """
    source_code = """
    int Result = 0b1111 & 0b1010;
    int Result2 = 0b1111 & 0b0101;
    int Result3 = 0b1111 & 0b0011;
    int Result4 = 0b1111 & 0b0000;
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]
    pyboy.stop()

    assert result == 0b1010

    teardown()


def test_right_shift():
    """
    End-to-end test for right shift operator (>>).
    """
    source_code = """
    int Result1 = 0b1111 >> 1;
    int Result2 = 0b1111 >> 2;
    int Result3 = 0b1111 >> 3;
    int Result4 = 0b1111 >> 4;
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result1 = pyboy.memory[data_segment_start]
    result2 = pyboy.memory[data_segment_start + 1]
    result3 = pyboy.memory[data_segment_start + 2]
    result4 = pyboy.memory[data_segment_start + 3]

    pyboy.stop()

    assert result1 == 0b0111
    assert result2 == 0b0011
    assert result3 == 0b0001
    assert result4 == 0b0000


def test_left_shift():
    """
    End-to-end test for left shift operator (<<).
    """
    source_code = """
    int Result1 = 0b0001 << 1;
    int Result2 = 0b0001 << 2;
    int Result3 = 0b0001 << 3;
    int Result4 = 0b0001 << 4;
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result1 = pyboy.memory[data_segment_start]
    result2 = pyboy.memory[data_segment_start + 1]
    result3 = pyboy.memory[data_segment_start + 2]
    result4 = pyboy.memory[data_segment_start + 3]

    pyboy.stop()

    assert result1 == 0b0010
    assert result2 == 0b0100
    assert result3 == 0b1000
    assert result4 == 0b10000


def test_loop_1():
    """
    End-to-end test for a loop with conditional logic.
    """
    source_code = """
    int Result = 0;
    int index = 0;

    loop (index < 5) {
        if (index == 3) {
            Result = Result + 10;
            index = 99; // Exit the loop
        } else {
            Result = Result + 1;
        }
        index = index + 1;
    }
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]
    pyboy.stop()

    assert result == 13

    teardown()


def test_binary_load_behavior():
    """
    End-to-end test for including binary files in rom
    """
    source_code = """
    tileset tileset_block_0 = "tileset_block_0.2bpp";
    tileset tileset_block_1 = "tileset_block_1.2bpp";
    tileset tileset_block_2 = "tileset_block_2.2bpp";
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    # read out rom_0 (0x0000 - 0x3FFF)
    rom_0 = pyboy.memory[0x0000:0x3FFF]

    pyboy.stop()

    # load in the binary files
    with open('temp_files/tileset_block_0.2bpp', 'rb') as f:
        tileset_block_0 = list(f.read())
    with open('temp_files/tileset_block_1.2bpp', 'rb') as f:
        tileset_block_1 = list(f.read())
    with open('temp_files/tileset_block_2.2bpp', 'rb') as f:
        tileset_block_2 = list(f.read())

    # convert to string for comparison
    tileset_block_0 = ''.join([chr(byte) for byte in tileset_block_0])
    tileset_block_1 = ''.join([chr(byte) for byte in tileset_block_1])
    tileset_block_2 = ''.join([chr(byte) for byte in tileset_block_2])
    rom_0 = ''.join([chr(byte) for byte in rom_0])

    assert tileset_block_0 in rom_0
    assert tileset_block_1 in rom_0
    assert tileset_block_2 in rom_0

    teardown()


def test_binary_load_to_vram_behavior():
    """
    End-to-end test for including binary files in rom, and loading them to VRAM
    """
    source_code = """
    tileset tileset_block_0 = "tileset_block_0.2bpp";
    tileset tileset_block_1 = "tileset_block_1.2bpp";
    tileset tileset_block_2 = "tileset_block_2.2bpp";
    
    control_waitVBlankStart();
    control_LCDoff();
    display_tileset_block_0 = tileset_block_0;
    display_tileset_block_1 = tileset_block_1;
    display_tileset_block_2 = tileset_block_2;
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    vram_tileset = pyboy.memory[0x8000:0x9800]

    pyboy.stop()
    # load in the binary files
    with open('temp_files/tileset_block_0.2bpp', 'rb') as f:
        tileset_block_0 = list(f.read())
    with open('temp_files/tileset_block_1.2bpp', 'rb') as f:
        tileset_block_1 = list(f.read())
    with open('temp_files/tileset_block_2.2bpp', 'rb') as f:
        tileset_block_2 = list(f.read())

    vram_tileset_blocks = [vram_tileset[i:i + 2048] for i in range(0, len(vram_tileset), 2048)]

    tileset_block_0 = ''.join([chr(byte) for byte in tileset_block_0])
    tileset_block_1 = ''.join([chr(byte) for byte in tileset_block_1])
    tileset_block_2 = ''.join([chr(byte) for byte in tileset_block_2])

    for i in range(len(vram_tileset_blocks)):
        vram_tileset_blocks[i] = ''.join([chr(byte) for byte in vram_tileset_blocks[i]])

    assert tileset_block_0 in vram_tileset_blocks
    assert tileset_block_1 in vram_tileset_blocks
    assert tileset_block_2 in vram_tileset_blocks

    teardown()


def test_load_binary_tilemap_to_vram_behavior():
    """
    End-to-end test for including binary files in rom, and loading them to VRAM
    """
    source_code = """
    tilemap tilemap0 = "tilemap_0.bin";
    control_waitVBlankStart();
    control_LCDoff();
    display_tilemap0 = tilemap0;
    control_LCDon();
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    vram_tilemap = pyboy.memory[0x9800:0x9C00]

    pyboy.stop()

    with open('temp_files/tilemap_0.bin', 'rb') as f:
        tilemap = list(f.read())

    tilemap = ''.join([chr(byte) for byte in tilemap])
    vram_tilemap = ''.join([chr(byte) for byte in vram_tilemap])

    assert tilemap in vram_tilemap

    teardown()


def test_function_call_inside_function_call():
    """
    End-to-end test for a function call inside function a call.
    """
    source_code = """
    procedure int Return_1() {
        return 1;
    }
    
    procedure int Return_3() {
        return 2 + Return_1();
    }

    int Result = 0;

    Result = Return_3();
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]
    pyboy.stop()

    assert result == 3

    teardown()


def test_linear_recursion():
    """
    End-to-end test for a recursive function.
    """
    source_code = """
    procedure int Recursive(int depth) {
        if (depth == 0) {
            return 0;
        } else {
            return 1 + Recursive(depth - 1);
        }
    }

    int Result = 0;

    Result = Recursive(20);
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]
    pyboy.stop()

    assert result == 20

    teardown()


def test_function_call_inside_loop():
    """
    End-to-end test for a function call inside a loop.
    """
    source_code = """
    procedure int Increment(int a) {
        return a + 1;
    }

    int Result = 0;
    int i = 0;

    loop (i < 5) {
        Result = Increment(Result);
        i = i + 1;
    }
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]
    pyboy.stop()

    assert result == 5

    teardown()


def test_input():
    """
    End-to-end test for input function.
    """
    source_code = """
    int Result = 0;

    control_updateInput();
    Result = control_checkLeft();
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')
    pyboy.button_press('left')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]

    assert result

    pyboy.stop()

    teardown()


def test_local_variable_in_procedure():
    """
    End-to-end test for local variable in procedure.
    """
    source_code = """
    int Result = 0;
    procedure int LocalVariableTest() {
        int test = 5;
        return 2;
    }

    Result = LocalVariableTest();
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]
    pyboy.stop()

    assert result == 2

    teardown()


def test_double_index_tilemap_store():
    """
    End-to-end test for doubly indexed tilemap.
    """
    source_code = """
    int Result = 0;
    tilemap tilemap0 = "tilemap_0.bin";
    
    control_waitVBlankStart();
    control_LCDoff();
    display_tilemap0 = tilemap0;
    
    control_LCDon();
    control_waitVBlankOver();
    control_waitVBlankStart();
    display_tilemap0[8][8] = 45;
    Result = display_tilemap0[8][8];
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    vram_tilemap = pyboy.memory[0x9800:0x9C00]
    result = vram_tilemap[8 * 32 + 8]
    result2 = pyboy.memory[data_segment_start]

    pyboy.stop()

    assert result == 45
    assert result2 == 45

    teardown()


def test_oam_index_tilemap_store():
    """
    End-to-end test for doubly indexed tilemap.
    """
    source_code = """
    int Result = 123;

    control_LCDon();
    control_waitVBlankOver();
    control_waitVBlankStart();

    display_oam_x[12] = 55;
    Result = display_oam_x[12];
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]

    pyboy.stop()

    assert result == 55

    teardown()


def test_if_else_in_procedure():
    """
    End-to-end test for if-else branching in a procedure and multiple procedures modifying the same global variable.
    """
    source_code = """
    int Result = 0;
    int Condition = 1;

    procedure test() {
        if (Condition == 1) {
            Result = 10;
        } else {
            Result = 20;
        }
    }
    
    procedure test2() {
        Result = Result + 10;
    }

    procedure main() {
        test();
        test2();
    }
    main();
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]

    pyboy.stop()

    assert result == 20

    teardown()


def test_procedure_return_nothing():
    """
    End-to-end test for a procedure that returns nothing.
    """
    source_code = """
    int Result = 0;

    procedure ReturnNothing() {
        return;
    }

    ReturnNothing();
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]
    pyboy.stop()

    assert result == 0

    teardown()


def test_fibonacci_recursive():
    """
    End-to-end test for recursion that calculates the 12th Fibonacci number.
    """
    source_code = """
    procedure int fibonacci(int n) {
        if (n == 0 or n == 1) {
            return n;
        } else {
            return fibonacci(n - 1) + fibonacci(n - 2);
        }
    }

    int Result = 0;

    Result = fibonacci(12);
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]

    pyboy.stop()

    assert result == 144

    teardown()
