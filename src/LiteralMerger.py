from src.astClasses import *
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

class LiteralMerger():
    def __init__(self):
        self.currentStatementIndex = 0

    def merge_node(self, node: ASTNode) -> ASTNode:
        logger.debug(f"Checking statement: {type(node).__name__}")
        
        method_name = f"merge_{node.__class__.__name__}"
        method = getattr(self, method_name, None)
        
        if method is None:
            logger.error(f"No type checking method for {type(node).__name__}")
            raise RuntimeError(f"No type checking method for {type(node).__name__}")
        
        return method(node)
    

    def merge_Program(self, node: Program) -> ASTNode:
        logger.info("Beginning literal merging")
        for stmt in node.statements:
            logger.info(f"Reached statement type {stmt.__class__}")
            node.statements[self.currentStatementIndex] = self.merge_node(stmt)
            self.currentStatementIndex += 1

        return node
    
    def merge_Declaration(self, node: Declaration) -> ASTNode:
        # Nothing to be merged in a declaration
        logger.info("Found a declaration, nothing to merge here")
        return node

    def merge_Assignment(self, node: Assignment) -> ASTNode:
        node.value = self.merge_node(node.value)
        node.target = self.merge_node(node.target)
        return node

    def merge_Initialization(self, node: Initialization) -> ASTNode:
        node.value = self.merge_node(node.value)
        return node

    def merge_Conditional(self, node: Conditional) -> ASTNode:
        node.condition = self.merge_node(node.condition)

        currentVal = 0
        for stmt in node.then_body:
            currentNode = self.merge_node(stmt)
            node.then_body[currentVal] = currentNode
            currentVal += 1

        if node.else_body:
            currentVal = 0
            for stmt in node.else_body:
                currentNode = self.merge_node(stmt)
                node.else_body[currentVal] = currentNode
                currentVal += 1

        return node
    def merge_Loop(self, node: Loop) -> ASTNode:
        node.condition = self.merge_node(node.condition)
        logger.info("Found proceduredef, checking body")
        currentVal = 0
        for stmt in node.body:
            currentNode = self.merge_node(stmt)
            node.body[currentVal] = currentNode
            currentVal += 1
        return node
    
    def merge_Return(self, node: Return) -> ASTNode: 
        node.value = self.merge_node(node.value)
        return node
    
    def merge_ProcedureCallStatement(self, node: ProcedureCallStatement) -> ASTNode:
        node.call = self.merge_node(node.call)
        return node
    
    def merge_ListAccess(self, node: ListAccess) -> ASTNode:
        currentIndex = 0
        for indice in node.indices:
            currentVal = self.merge_node(indice)
            if currentVal:
                node.indices[currentIndex] = currentVal
            currentIndex += 1

        return node

    def merge_BinaryOp(self, node: BinaryOp) -> ASTNode:
        logger.info("Found binary expression, attempting merge")
        node.left = self.merge_node(node.left)
        node.right = self.merge_node(node.right)
        if (isinstance(node.left, IntegerLiteral) and isinstance(node.right, IntegerLiteral)):
            return self.mergeBinary(node)
            
        return node
    
    def merge_UnaryOp(self, node: BinaryOp) -> ASTNode:
        logger.info("Found unary expression, attempting merge")
        node.operand = self.merge_node(node.operand)
        if isinstance(node.operand, IntegerLiteral):
            return self.mergeUnary(node)
            
        return node
    
    def merge_IntegerLiteral(self, node: IntegerLiteral) -> ASTNode:
        logger.info("Found Integer literal, returning")
        return node
    
    def merge_StringLiteral(self, node: StringLiteral) -> ASTNode:
        logger.info("Found string literal, inside statement that cannot be merged")
        return node
    
    def merge_ProcedureCall(self, node: ProcedureCall) -> ASTNode:
        logger.info("Found procedurecall, checking params")
        currentVal = 0
        for stmt in node.params:
            currentNode = self.merge_node(stmt)
            node.params[currentVal] = currentNode
            currentVal += 1
        
        return node
    
    def merge_ProcedureDef(self, node: ProcedureDef) -> ASTNode:
        logger.info("Found proceduredef, checking body")
        currentVal = 0
        for stmt in node.body:
            currentNode = self.merge_node(stmt)
            node.body[currentVal] = currentNode
            currentVal += 1
        
        return node
    
    def merge_Variable(self, node: Variable) -> ASTNode:
        return node
    
    def mergeBinary(self, node: BinaryOp) -> ASTNode:
        # Prob could be done in a simpler manner by simply translating the operator,
        # but in case of future operators that dont match any Python math, this is how we do it
        left_val = int(node.left.value)
        right_val = int(node.right.value)

        def to_8bit(value):
            return value & 0xFF
    
        # Ensure operands are in 8-bit range
        left = to_8bit(left_val)
        right = to_8bit(right_val)

        result = 0

        match node.op:
            case '+':
                result = to_8bit(left + right)
            case '-':
                result = to_8bit(left - right)
            case '*':
                result = to_8bit(left * right)
            case '==':
                result = int(left == right)
            case '!=':
                result = int(left != right)
            case '&':
                result = left & right 
            case 'and':
                result = int((left != 0) and (right != 0))
            case '|':
                result = left | right 
            case 'or':
                result = int((left != 0) or (right != 0))
            case '^':
                result = left ^ right
            case '>':
                result = int(left > right)
            case '<':
                result = int(left < right)
            case '<=':
                result = int(left <= right)
            case '>=':
                result = int(left >= right)
            case '<<':
                result = to_8bit(left << right)
            case '>>':
                result = left >> right 
            case _:
                logger.error("Binary statement case not found, could not merge binary expression with two integer literals")
                logger.info("Returning original node")
                return node
            
        return IntegerLiteral((result))
        


    def mergeUnary(self, node: UnaryOp) -> ASTNode:
        match node.op:
            case '~':
                logger.info("Not implemented yet")
                return node
            case 'not':
                logger.info("Not implemented yet")
                return node
            case _:
                logger.error("Binary statement case not found, could not merge binary expression with two integer literals")
                logger.info("Returning original node")
                return node