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

    def merge_node(self, node: ASTNode) -> ASTNode:
        logger.debug(f"Checking statement: {type(node).__name__}")
        
        method_name = f"merge_{node.__class__.__name__}"
        method = getattr(self, method_name, None)
        
        if method is None:
            logger.error(f"No type checking method for {type(node).__name__}")
            raise RuntimeError(f"No type checking method for {type(node).__name__}")
        
        return method(node)
    

    def merge_Program(self, node: Program):
        logger.info("Beginning literal merging")
        for stmt in node.statements:
            logger.info(f"Reached statement type {stmt.__class__}")
            if stmt.__class__ in self.statementTypesToCheck:
                logger.info(f"Found class {stmt.__class__}, proceding to check expressions")

    def merge_Declaration(self, node: Declaration) -> ASTNode:
        # Nothing to be merged in a declaration
        logger.info("Found a declaration, nothing to merge here")
        return node

    def merge_Assignment(self, node: Assignment) -> ASTNode:
        node.value = self.merge_node(node.value)
        node.target = self.merge_node(node.target)


    def merge_Initialization(self, node: Initialization) -> ASTNode:
        node.value = self.checkExpression(node.value)
         
    def merge_Conditional(self, node: Conditional) -> ASTNode:
             node.condition 
    def merge_Loop(self, node: Loop) -> ASTNode:
    
    def merge_Return(self, node: Return) -> ASTNode: 
                 
    def merge_ProcedureCallStatement(self, node: ProcedureCallStatement) -> ASTNode:
    
    def merge_ListAccess(self, node: ListAccess) -> ASTNode:
        if isinstance(node.target, ListAccess):
            currentIndex = 0
            for indice in node.target.indices:
                currentVal = self.merge_node(indice)
                if currentVal:
                    node.target.indices[currentIndex] = currentVal
                currentIndex += 1

    def merge_BinaryOp(self, node: BinaryOp):
        logger.info("Found binary expression, attempting merge")
        node.left = self.checkExpression(node.left)
        node.right = self.checkExpression(node.right)
        if (isinstance(node.left, IntegerLiteral) and isinstance(node.right, IntegerLiteral)):
            return self.MergeBinary(node)
            
        return node
    
    def merge_UnaryOp(self, node: BinaryOp):
        logger.info("Found unary expression, attempting merge")
        node.operand = self.checkExpression(node.operand)
        if isinstance(node.operand, IntegerLiteral):
            return self.MergeUnary(node)
            
        return node
    
    def merge_IntegerLiteral(self, node: IntegerLiteral):
        logger.info("dflgædfkl")
        return node