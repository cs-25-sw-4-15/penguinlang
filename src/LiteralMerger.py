from src.astClasses import *
from astTypes import *
import os
import sys
from typing import List, Tuple, Union, Optional, Dict
from src.logger import logger

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class LiteralMerger():
    def __init__(self):
        self.currentVar = ""

    def mergeLiterals(self, node: ASTNode):
        logger.info("Logging ")
        
