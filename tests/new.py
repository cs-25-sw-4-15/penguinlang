import pytest
import sys
import os

from src.compiler import *


class TestASTGenerator:
    def test_visit(self, ast_gen):
        """Test the visit method of the ASTGenerator class."""
        input_data = {
            "type": "Program",
            "body": [
                {
                    "type": "FunctionDeclaration",
                    "id": {"type": "Identifier", "name": "main"},
                    "params": [],
                    "body": {"type": "BlockStatement", "body": []},
                }
            ],
        }
        result = ast_gen.visit(input_data)
        assert isinstance(result, ASTNode)
    
    
class TestTAASTChecker:
    ...
    