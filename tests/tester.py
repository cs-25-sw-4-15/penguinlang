import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the test modules
from tests.src.astTests import *
from tests.src.taastTests import *

if __name__ == "__main__":
    pytest.main()
