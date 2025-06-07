from src.astClasses import *
from astTypes import *
import os
import sys
from typing import List, Tuple, Union, Optional, Dict
from src.logger import logger

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

"""
1. Visit every statement
2. Check each value in the statement
3. For the value, if consisting of two literals, merge
4. Else, if contains more expressions, check those (recursive?)
5. Else, if contains runtime shit (Vars, hardware shit), ignore, gg go next
"""

class LiteralMergerChecker():
    def __init__(self):
        self.statementTypesToCheck = {Assignment, Initialization, Conditional, Loop, Return, ProcedureCall, ListAccess}
        self.ExpressionTypes = {BinaryOp, UnaryOp}

    def mergeProgram(self, node: Program):
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
    
    def merge_Assignment(self, node: Assignment):
        valueMerged = self.checkExpression(node.value)
        if valueMerged:
            node.value = valueMerged

        if isinstance(node.target, ListAccess):
            currentIndex = 0
            for indice in node.target.indices:
                currentVal = self.checkExpression(indice)
                if currentVal:
                    node.target.indices[currentIndex] = currentVal
                currentIndex += 1

    def merge_Initialization(self, node: Initialization):
         
    def merge_Conditional(self, node: Conditional):
             
    def merge_Loop(self, node: Loop):
    
    def merge_Return(self, node: Return): 
                 
    def merge_ProcedureCall(self, node: ProcedureCall):
    
    def merge_ListAccess(self, node: ListAccess):

    def checkExpression(self, node: ASTNode) -> ASTNode:
        if isinstance(node, BinaryOp):
            logger.info("Found binary expression, attempting merge")
            node.left = self.checkExpression(node.left)
            node.right = self.checkExpression(node.right)
            if (isinstance(node.left, IntegerLiteral) and isinstance(node.right, IntegerLiteral)):
                return self.MergeBinary(node)
            
            return node
            
        elif isinstance(node, UnaryOp):
            logger.info("Found unary expression, attempting merge")
            node.operand = self.checkExpression(node.operand)
            if isinstance(node.operand, IntegerLiteral):
                return self.MergeUnary(node)
            
            return node

        elif isinstance(node, IntegerLiteral):
            return node
        
        else:
            logger.info(f"Did not find an expression, instead found {node.__class__}, returning from merging")
            return node
    
    def mergeBinary(self, node) -> IntegerLiteral:
        logger.info("Found binary expression, attempting merge")
        
    def mergeUnary(self, node) -> IntegerLiteral:
        logger.info("Found binary expression, attempting merge")