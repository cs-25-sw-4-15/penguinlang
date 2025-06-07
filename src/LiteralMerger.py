from src.astClasses import *
from astTypes import *
import os
import sys
from typing import List, Tuple, Union, Optional, Dict
from src.logger import logger

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class LiteralMerger():
    def __init__(self):
        self.statementTypesToCheck = {Assignment, Initialization, Conditional, Loop, Return, ProcedureCall, ListAccess}
        self.ExpressionTypes = {BinaryOp, UnaryOp}

    def mergeLiterals(self, node: Program):
        logger.info("Beginning literal merging")
        for stmt in node.statements:
            logger.info(f"Reached statement type {stmt.__class__}")
            if stmt.__class__ in self.statementTypesToCheck:
                logger.info(f"Found class {stmt.__class__}, proceding to check expressions")
                result = self.merge_node(stmt)
                if(result):
                    logger.info("Successfully merged literals inside statement!")
                else:
                    logger.info("Did not find any possible literal merging inside statement")


    def merge_node(self, node: ASTNode) -> bool:
        logger.debug(f"Checking statement: {type(node).__name__}")
        
        method_name = f"merge_{node.__class__.__name__}"
        method = getattr(self, method_name, None)
        
        if method is None:
            logger.error(f"No type checking method for {type(node).__name__}")
            raise RuntimeError(f"No type checking method for {type(node).__name__}")
        
        return method(node)
    
    def merge_Assignment(self, node: ASTNode):
     
    def merge_Initialization(self, node: ASTNode):
         
    def merge_Conditional(self, node: ASTNode):
             
    def merge_Loop(self, node: ASTNode):
    
    def merge_Return(self, node: ASTNode): 
                 
    def merge_ProcedureCall(self, node: ASTNode):
    
    def merge_ListAccess(self, node: ASTNode):

    def checkExpression(self, node: ASTNode):
        if node.__class__ == BinaryOp.__class__:
            logger.info("Found binary expression, attempting merge")

        else if node.__class__ == UnaryOp.__class__:

        else if node.__class__ == BinaryOp.__class__:

        else if node.__class__ == Variable.__class__:



    

