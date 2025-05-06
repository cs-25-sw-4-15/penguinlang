import unittest
from pyboy import PyBoy


class Romtest(unittest.TestCase):
    def test_rom(self):

        pyboy = PyBoy('roms/rom_test_example.gb', window='null')

        while(pyboy.register_file.PC != 0x0155):
            pyboy.tick()

        value = pyboy.register_file.A
        pyboy.stop()

        self.assertEqual(value, 2)


if __name__ == '__main__':
    unittest.main()
