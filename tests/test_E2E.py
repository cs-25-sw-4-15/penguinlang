import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import glob
from pyboy import PyBoy
from src.compiler import full_compile

data_segment_start = 0xC000
program_start = 0x0150


def loop_detected(pyboy, PC_list):
    """
    Detects if the program is in a loop by checking if the PC has repeated.
    """
    if pyboy.register_file.PC in PC_list:
        return True
    else:
        current_pc = pyboy.register_file.PC
        if current_pc >= program_start:
            PC_list.append(current_pc)
        return False


def nop_reached(pyboy):
    """
    Detects if the program has reached a NOP instruction.
    """
    return pyboy.memory[pyboy.register_file.PC] == 0x00


def compile_source_to_binary(source_code: str, output_dir: str = 'temp_files') -> str:
    """
    Compiles the given source code into a binary file and returns the path to the binary.

    Args:
        source_code (str): The source code to compile.
        output_dir (str): The directory to store the compiled binary.

    Returns:
        str: The path to the compiled binary file.
    """
    os.makedirs(output_dir, exist_ok=True)
    source_file_path = os.path.join(output_dir, 'temp_source.peg')
    binary_file_path = os.path.join(output_dir, 'temp_binary.gb')

    # copy test_files to temp_files
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
    """
    Cleans up the test environment by resetting global variables and removing files in the 'temp_files' directory.
    """
    global PC_list, pyboy
    PC_list = []
    pyboy = None

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
    int Result = 0;
    int Integer1 = 5;

    int Integer2 = 1;

    Result = Integer1 + (Integer2 + 3);
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]
    pyboy.stop()

    assert result == 9

    teardown()


def test_subtraction_1():
    """
    End-to-end test for simple subtraction operation.
    """
    source_code = """
    int Result = 0;
    int Integer1 = 100;

    int Integer2 = 10;

    Result = Integer1 - (Integer2 - 3);
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]
    pyboy.stop()

    assert result == 93

    teardown()


@pytest.mark.xfail(reason="not implemented")
def test_multiplication_1():
    """
    End-to-end test for simple multiplication operation.
    """
    source_code = """
    int Result = 0;
    int Integer1 = 6;

    int Integer2 = 7;

    Result = Integer1 * Integer2;
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]
    pyboy.stop()

    assert result == 42

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


def test_if_else_if_branch():
    """
    End-to-end test for if-else-if branching.
    """
    source_code = """
    int Result = 0;
    int Condition = 2;

    if (Condition == 1) {
        Result = 10;
    } else if (Condition == 2) {
        Result = 20;
    } else {
        Result = 30;
    }
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]
    pyboy.stop()

    assert result == 20

    teardown()


def test_equality_and_inequality():
    """
    End-to-end test for equality (==) and inequality (!=) operators.
    """
    source_code = """
    int Result = 0;
    int A = 5;
    int B = 5;
    int C = 10;

    if (A == B) {
        Result = 1;
    }

    if (A != C) {
        Result = Result + 1;
    }
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]
    pyboy.stop()

    assert result == 2

    teardown()


def test_comparisons():
    """
    End-to-end test for comparison operators (<, >, <=, >=).
    """
    source_code = """
    int Result = 0;
    int A = 5;
    int B = 10;

    if (A < B) {
        Result = 1;
    }

    if (B > A) {
        Result = Result + 1;
    }

    if (A <= 5) {
        Result = Result + 1;
    }

    if (B >= 10) {
        Result = Result + 1;
    }
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]
    pyboy.stop()

    assert result == 4

    teardown()


@pytest.mark.xfail(reason="dropped attributes")
def test_logical_operators():
    """
    End-to-end test for logical operators (and, or, not).
    """
    source_code = """
    int Result = 0;
    int A = 1;
    int B = 0;

    if (A and (not B)) {
        Result = 1;
    }

    if (A or B) {
        Result = Result + 1;
    }
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]
    pyboy.stop()

    assert result == 2

    teardown()


def test_bitwise_shifts():
    """
    End-to-end test for left (<<) and right (>>) shift operators.
    """
    source_code = """
    int Result = 0;
    int A = 4; // Binary: 0100

    Result = A << 1; // Left shift by 1, Result: 1000 (8)
    Result = Result >> 2; // Right shift by 2, Result: 0010 (2)
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]
    pyboy.stop()

    assert result == 2

    teardown()


@pytest.mark.xfail(reason="dropped attributes")
def test_bitwise_logical_operators():
    """
    End-to-end test for bitwise logical operators (&, |, ^, ~).
    """
    source_code = """
    int Result = 0;
    int A = 6;  // Binary: 0110
    int B = 3;  // Binary: 0011

    Result = A & B;  // Bitwise AND, Result: 0010 (2)
    Result = Result | B;  // Bitwise OR, Result: 0011 (3)
    Result = Result ^ A;  // Bitwise XOR, Result: 0101 (5)
    Result = ~Result;  // Bitwise NOT, Result: ...1010 (Two's complement representation)
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    result = pyboy.memory[data_segment_start]
    pyboy.stop()

    # Assuming 8-bit signed integers, ~5 would result in -6
    assert result == -6

    teardown()


def test_loop_behavior():
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

    # The loop should add 1 for index 0, 1, 2, and 10 for index 3, then exit.
    assert result == 13

    teardown()


def test_binary_load_behavior():
    """
    End-to-end test for including binary files in rom
    """
    source_code = """
    tileset tileset1 = "tileset.2bpp";
    """

    binary_path = compile_source_to_binary(source_code)
    pyboy = PyBoy(binary_path, window='null')

    while not nop_reached(pyboy):
        pyboy.tick()

    # read out rom_0 (0x0000 - 0x3FFF)
    rom_0 = pyboy.memory[0x0000:0x3FFF]

    pyboy.stop()

    # load in the binary file
    with open('temp_files/tileset.2bpp', 'rb') as f:
        binary_data = list(f.read())

    # convert to string for comparison
    binary_data = ''.join([chr(byte) for byte in binary_data])
    rom_0 = ''.join([chr(byte) for byte in rom_0])

    assert binary_data in rom_0

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


# TODO: add tests for built-in functions, binary handling and the like, tileset, tilemaps, screen rendering, etc.
