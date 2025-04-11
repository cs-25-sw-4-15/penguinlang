from ast import *

# Generated modules
from generated.penguinParser import penguinParser
from generated.penguinVisitor import penguinVisitor

# Custom modules
from ast_classes import ASTNode, \
    Program, \
    Declaration, Assignment, Initialization, ListInitialization, Conditional, Loop, Return, ProcedureCallStatement, \
    BinaryOp, UnaryOp, IntegerLiteral, StringLiteral, ProcedureCall, Variable, ListAccess, AttributeAccess, \
    ProcedureDef

from custom_errors import UnknownExpressionTypeError, UnknownValueTypeError, UnknowninitializationTypeError, UnknownLiteralTypeError

# Typing modules
from typing import List, Tuple, Union, Any, Optional

# Logging modules
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from PredefinedFsAndVs import initialize_hardware_elements


#Start med at modtage det tree som vi har lavet i AST generator

#Vi skal også imens vi gennemløber, tjekke om typerne i procedure kald er OK, og om variablerne er defineret / erklæret. Aka, liste over alle de forskellige variabler, lister, attributes (Gælder kun registers)
#Det samme gælder funktioner, men vi skal nok løbe dem igennem først, da funktionskald gerne skulle kunne placeres hvor end.

#Den skal nok køre et loop igennem de forskellige statements? Det giver ikke mening at lade tjekke om program er OK ud fra de forskellige statements, ikke engang alle statements behøver at blie tjekket
#Brug visitor pattern eller generic recursive function til at besøge alle noderne, 
# og fra bunden så finde den nuværende nodes typer, underliggende, på den vis at lade typen florere op

#I løbet af denne process, bliver semantikken tjekket om den er OK, 
#ift. godtagning af de forskellige nodes der tjekkes, efter alle childrens typer er gået op i træet

#Efter denne gennemløbning, kan vi returnere det samme træ som vi arbejdede på, da vi kun ændrer typerne på det.
#Kører det igennem uden fejl, er der ingen semantiske fejl, og det er nu et TAAST



#OKAY MERE KONKRET

#Gennemløb erklæringer / definitioner af variabler og funktioner, og tilføj dem til en liste der OGSÅ indeholder hardware registers
#Typetjek dem imens?

"""Type Checker for the Penguin Language

Traverses an AST and verifies type correctness according to language rules.
"""

# Create a base Type class
class Type:
    """Base class for all types in the type system."""
    
    def __eq__(self, other):
        """Check if two types are equal."""
        if not isinstance(other, Type):
            return False
        return type(self) == type(other)
    
    def __repr__(self):
        """String representation of the type."""
        return self.__class__.__name__

# Import the provided type classes
from asttypes import IntType, StringType, VoidType, ListType, TilesetType, TileMapType, SpriteType, OAMEntryType

# Type errors
class TypeError(Exception):
    """Base class for type errors."""
    pass

class TypeMismatchError(TypeError):
    """Error for when types don't match."""
    pass

class UndeclaredVariableError(TypeError):
    """Error for when a variable is used but not declared."""
    pass

class DuplicateDeclarationError(TypeError):
    """Error for when a variable is declared multiple times."""
    pass

class InvalidTypeError(TypeError):
    """Error for when an invalid type is used."""
    pass

class TypeChecker:
    """Type checker for Penguin Language AST.
    
    Traverses an AST and verifies type correctness according to language rules.
    """
    
    def __init__(self):
        self.symbol_table: Dict[str, Type] = {}  # Maps variable names to their types
        self.procedure_table: Dict[str, Tuple[List[Tuple[str, Type]], Type]] = {}  # Maps procedure names to (param_types, return_type)
        self.current_return_type: Optional[Type] = None  # Return type of the current procedure
        
        # Set up logging
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        
        # Initialize predefined hardware elements
        self._init_predefined_elements()
    
    def _init_predefined_elements(self):
        """Initialize predefined hardware modules, variables, and functions."""
        # Get predefined elements from the hardware module
        hardware_symbols, hardware_procedures = initialize_hardware_elements()
        
        # Add predefined symbols to the symbol table
        self.symbol_table.update(hardware_symbols)
        
        # Add predefined procedures to the procedure table
        self.procedure_table.update(hardware_procedures)
        
        self.logger.info(f"Initialized {len(hardware_symbols)} hardware symbols and {len(hardware_procedures)} hardware procedures")
    
    def string_to_type(self, type_str: str) -> Type:
        """Convert a type string to a Type object."""
        self.logger.debug(f"Converting string '{type_str}' to type")
        
        if type_str == "int" or type_str == "Int":
            return IntType()
        elif type_str == "Tileset" or type_str == "tileset":
            return TilesetType()
        elif type_str == "Tilemap" or type_str == "tilemap":
            return TileMapType()
        elif type_str == "Sprite" or type_str == "sprite":
            return SpriteType()
        elif type_str == "String" or type_str == "string":
            return StringType()
        elif type_str == "void":
            return VoidType()
        else:
            raise InvalidTypeError(f"Invalid type: {type_str}")
    
    def check_program(self, node: Program) -> None:
        """Type check a Program node."""
        self.logger.info("Type checking program")
        
        # Type check each statement in the program
        for statement in node.statements:
            self.check_node(statement)
    
    def check_node(self, node: ASTNode) -> Type:
        """Type check an AST node by dispatching to the appropriate method."""
        self.logger.debug(f"Type checking node: {type(node).__name__}")
        
        # Use a method dispatch pattern to call the appropriate check method
        method_name = f"check_{node.__class__.__name__}"
        method = getattr(self, method_name, None)
        
        if method is None:
            self.logger.error(f"No type checking method for {type(node).__name__}")
            raise TypeError(f"No type checking method for {type(node).__name__}")
        
        return method(node)
    
    def check_Declaration(self, node: Declaration) -> None:
        """Type check a Declaration node."""
        self.logger.info(f"Type checking declaration: {node.name} of type {node.var_type}")
        
        # Check if the variable has already been declared
        if node.name in self.symbol_table:
            raise DuplicateDeclarationError(f"Variable '{node.name}' already declared")
        
        # Convert the type string to a Type object
        var_type = self.string_to_type(node.var_type)
        
        # Add the variable to the symbol table
        self.symbol_table[node.name] = var_type

        node.var_type = var_type  # Store the type in the node for later use
        
        self.logger.debug(f"Declared variable '{node.name}' with type {var_type}")
    
    def check_Assignment(self, node: Assignment) -> None:
        """Type check an Assignment node."""
        self.logger.info(f"Type checking assignment: {node.target}")
        
        # Type check the target and value
        target_type = self.check_node(node.target)
        value_type = self.check_node(node.value)
        
        node.var_type = target_type
          # Store the type in the node for later use
        # Check if the types match
        if target_type != value_type:   
            if(value_type == SpriteType() and target_type == IntType()):
                return
            self.logger.error(f"Type mismatch in assignment: expected {target_type}, got {value_type}")
            raise TypeMismatchError(f"Type mismatch in assignment: expected {target_type}, got {value_type}")

        if(target_type == (TileMapType, TilesetType, SpriteType)):
            #Special case, where the above types cannot be reassigned at runtime
            self.logger.error(f"Cannot reassign {target_type} at runtime")
            raise TypeMismatchError(f"Cannot reassign {target_type} at runtime")
        
        self.logger.debug(f"Assigned {node.value} to {node.target}")

    def check_Initialization(self, node: Initialization) -> None:
        """Type check an Initialization node."""
        self.logger.info(f"Type checking initialization: {node.name} of type {node.var_type}")
        
        # Check if the variable has already been declared
        if node.name in self.symbol_table:
            raise DuplicateDeclarationError(f"Variable '{node.name}' already declared")
        
        # Convert the type string to a Type object
        var_type = self.string_to_type(node.var_type)
        
        # Add the variable to the symbol table
        self.symbol_table[node.name] = var_type
        
        # Type check the value
        value_type = self.check_node(node.value)
        node.var_type = var_type  # Store the type in the node for later use
        # Check if the types match
        if var_type != value_type:
            # Special case for Tileset, TileMap, and Sprite which must be assigned strings
            if (isinstance(var_type, (TilesetType, TileMapType, SpriteType)) and 
                isinstance(value_type, StringType)):
                return
            
            self.logger.error(f"Type mismatch in initialization: expected {var_type}, got {value_type}")
            raise TypeMismatchError(f"Type mismatch in initialization: expected {var_type}, got {value_type}")
    
    def check_ListInitialization(self, node: ListInitialization) -> None:
        """Type check a ListInitialization node."""
        self.logger.info(f"Type checking list initialization: {node.name}")
        
        # Check if the variable has already been declared
        if node.name in self.symbol_table:
            raise DuplicateDeclarationError(f"Variable '{node.name}' already declared")
        
        # Per the rules, lists must always be of type int
        list_type = ListType(IntType())
        
        # Add the variable to the symbol table
        self.symbol_table[node.name] = list_type
        node.var_type = ListType()  # Store the type in the node for later use
        # Type check each value in the list
        for value in node.values:
            value_type = self.check_node(value)
            if value_type != IntType():
                self.logger.error(f"Type mismatch in list initialization: expected int, got {value_type}")
                raise TypeMismatchError(f"Type mismatch in list initialization: expected int, got {value_type}")
    
    def check_Conditional(self, node: Conditional) -> Type:
        """Type check a Conditional node."""
        self.logger.info("Type checking conditional statement")
        
        # Type check the condition
        condition_type = self.check_node(node.condition)
        
        # Check if the condition evaluates to a boolean (represented as int in this language)
        if not isinstance(condition_type, IntType):
            self.logger.error(f"Condition must be of type int, got {condition_type}")
            raise TypeMismatchError(f"Condition must be of type int, got {condition_type}")
        
        # Type check the then body
        for statement in node.then_body:
            self.check_node(statement)
        
        # Type check the else body if it exists
        if node.else_body:
            for statement in node.else_body:
                self.check_node(statement)
        
        return VoidType()
    
    def check_Loop(self, node: Loop) -> Type:
        """Type check a Loop node."""
        self.logger.info("Type checking loop")
        
        # Type check the condition
        condition_type = self.check_node(node.condition)
        
        # Check if the condition evaluates to a boolean (represented as int in this language)
        if not isinstance(condition_type, IntType):
            self.logger.error(f"Loop condition must be of type int, got {condition_type}")
            raise TypeMismatchError(f"Loop condition must be of type int, got {condition_type}")
        
        # Type check the body
        for statement in node.body:
            self.check_node(statement)
        
        return VoidType()
    
    def check_Return(self, node: Return) -> Type:
        """Type check a Return node."""
        self.logger.info("Type checking return statement")
        
        # Type check the return value
        value_type = self.check_node(node.value)
        node.var_type = value_type  # Store the type in the node for later use 
        # Check if the return type matches the current procedure's return type
        if self.current_return_type is None:
            self.logger.error("Return statement outside of procedure")
            raise TypeError("Return statement outside of procedure")
        
        if value_type != self.current_return_type:
            self.logger.error(f"Return type mismatch: expected {self.current_return_type}, got {value_type}")
            raise TypeMismatchError(f"Return type mismatch: expected {self.current_return_type}, got {value_type}")
        
        return value_type
    
    def check_ProcedureCallStatement(self, node: ProcedureCallStatement) -> Type:
        """Type check a ProcedureCallStatement node."""
        self.logger.info("Type checking procedure call statement")
        
        # Type check the procedure call
        self.check_node(node.call)
        
        return VoidType()
    
    def check_BinaryOp(self, node: BinaryOp) -> Type:
        """Type check a BinaryOp node."""
        self.logger.info(f"Type checking binary operation: {node.op}")
        
        # Type check the left and right operands
        left_type = self.check_node(node.left)
        right_type = self.check_node(node.right)
        
        node.var_type = right_type  # Store the type in the node for later use
        # Check operator compatibility
        if node.op in ['+', '-', '*']:
            # Arithmetic operators
            if not isinstance(left_type, IntType) or not isinstance(right_type, IntType):
                self.logger.error(f"Arithmetic operator '{node.op}' requires integer operands, got {left_type} and {right_type}")
                raise TypeMismatchError(f"Arithmetic operator '{node.op}' requires integer operands, got {left_type} and {right_type}")
            return IntType()
        
        elif node.op in ['<', '>', '<=', '>=', '==', '!=']:
            # Comparison operators
            if not isinstance(left_type, IntType) or not isinstance(right_type, IntType):
                self.logger.error(f"Comparison operator '{node.op}' requires integer operands, got {left_type} and {right_type}")
                raise TypeMismatchError(f"Comparison operator '{node.op}' requires integer operands, got {left_type} and {right_type}")
            return IntType()  # Comparison returns boolean (represented as int)
        
        elif node.op in ['&&', '||']:
            # Logical operators
            if not isinstance(left_type, IntType) or not isinstance(right_type, IntType):
                self.logger.error(f"Logical operator '{node.op}' requires integer operands, got {left_type} and {right_type}")
                raise TypeMismatchError(f"Logical operator '{node.op}' requires integer operands, got {left_type} and {right_type}")
            return IntType()
        
        elif node.op in ['>>', '<<', '&', '|', '^']:
            # Logical operators
            if not isinstance(left_type, IntType) or not isinstance(right_type, IntType):
                self.logger.error(f"Logical operator '{node.op}' requires integer operands, got {left_type} and {right_type}")
                raise TypeMismatchError(f"Logical operator '{node.op}' requires integer operands, got {left_type} and {right_type}")
            return IntType()
        
        elif node.op in ['and', 'or']:
            # Logical operators
            if not isinstance(left_type, IntType) or not isinstance(right_type, IntType):
                self.logger.error(f"Logical operator '{node.op}' requires integer operands, got {left_type} and {right_type}")
                raise TypeMismatchError(f"Logical operator '{node.op}' requires integer operands, got {left_type} and {right_type}")
            return IntType()
        
        else:
            self.logger.error(f"Unknown binary operator: {node.op}")
            raise TypeError(f"Unknown binary operator: {node.op}")
    
    def check_UnaryOp(self, node: UnaryOp) -> Type:
        """Type check a UnaryOp node."""
        self.logger.info(f"Type checking unary operation: {node.op}")
        
        # Type check the operand
        operand_type = self.check_node(node.operand)
        
        # Check operator compatibility
        if node.op in ['-', '!', '~', 'not']:
            if not isinstance(operand_type, IntType):
                self.logger.error(f"Unary operator '{node.op}' requires integer operand, got {operand_type}")
                raise TypeMismatchError(f"Unary operator '{node.op}' requires integer operand, got {operand_type}")
            node.var_type = IntType()  # Store the type in the node for later use
            return IntType()
        
        else:
            self.logger.error(f"Unknown unary operator: {node.op}")
            raise TypeError(f"Unknown unary operator: {node.op}")
    
    def check_IntegerLiteral(self, node: IntegerLiteral) -> Type:
        """Type check an IntegerLiteral node."""
        self.logger.debug(f"Integer literal: {node.value}")
        node.var_type = IntType()  # Store the type in the node for later use
        return IntType()
    
    def check_StringLiteral(self, node: StringLiteral) -> Type:
        """Type check a StringLiteral node."""
        self.logger.debug(f"String literal: {node.value}")
        node.var_type = StringType()  # Store the type in the node for later use
        return StringType()
    
    def check_Variable(self, node: Variable) -> Type:
        """Type check a Variable node."""
        self.logger.info(f"Type checking variable: {node.name}")
        
        # Handle the case where node.name is an AttributeAccess instance
        if isinstance(node.name, AttributeAccess):
            # When Variable contains an AttributeAccess, we should just check the AttributeAccess
            var_type = self.check_AttributeAccess(node.name)
            node.var_type = var_type
            return self.check_node(node.name)
        
        # Regular case - node.name is a string
        if node.name not in self.symbol_table:
            self.logger.error(f"Undeclared variable: {node.name}")
            raise UndeclaredVariableError(f"Undeclared variable: {node.name}")
        
        # Return the variable's type
        var_type = self.symbol_table[node.name]
        node.var_type = var_type
        return self.symbol_table[node.name]
    
    def check_ListAccess(self, node: ListAccess) -> Type:
        """Type check a ListAccess node."""
        self.logger.info(f"Type checking list access: {node.name}")
        node.var_type = IntType()  # Store the type in the node for later use
        
        # Get the base object to check if it's indexable
        if isinstance(node.name, str):
            if node.name not in self.symbol_table:
                self.logger.error(f"Undeclared variable: {node.name}")
                raise UndeclaredVariableError(f"Undeclared variable: {node.name}")
            
            base_type = self.symbol_table[node.name]
        else:
            # If node.name is not a string, it's a nested structure (like a.b[0])
            base_type = self.check_node(node.name)
        
        # Check if the base object is indexable
        if not base_type.is_indexable():
            self.logger.error(f"Type {base_type} is not indexable")
            raise TypeMismatchError(f"Type {base_type} is not indexable")
        
        # Type check each index
        for index in node.indices:
            index_type = self.check_node(index)
            if not isinstance(index_type, IntType):
                self.logger.error(f"Index must be of type int, got {index_type}")
                raise TypeMismatchError(f"Index must be of type int, got {index_type}")
        
        # Return the type of element that we get when indexing this type
        return base_type.index_result_type()

    
    def check_AttributeAccess(self, node: AttributeAccess) -> Type:
        """Type check an AttributeAccess node."""
        self.logger.info(f"Type checking attribute access: {node.attribute} on {node.name}")
        
        # Handle predefined complex paths
        full_path = ""
        if isinstance(node.name, str):
            full_path = f"{node.name}.{node.attribute}"
        elif isinstance(node.name, AttributeAccess):
            # Handle nested AttributeAccess
            if isinstance(node.name.name, str):
                base_name = node.name.name
            elif hasattr(node.name.name, 'name'):
                base_name = node.name.name.name
            else:
                base_name = str(node.name.name)
            full_path = f"{base_name}.{node.name.attribute}.{node.attribute}"
        elif hasattr(node.name, 'name'):
            full_path = f"{node.name.name}.{node.attribute}"
        else:
            full_path = f"{node.name}.{node.attribute}"
        
        # Check if we have a predefined path
        if full_path in self.symbol_table:
            return self.symbol_table[full_path]
        
        # Get the base object type
        base_obj = self.check_node(node.name) if isinstance(node.name, ASTNode) else self.symbol_table.get(node.name)
        
        if base_obj is None:
            self.logger.error(f"Undeclared variable: {node.name}")
            raise UndeclaredVariableError(f"Undeclared variable: {node.name}")
        
        # Special case for when node.name is a ListAccess
        if isinstance(node.name, ListAccess):
            # If this is a list access, get the element type from the list type
            list_type = self.check_node(node.name)
            
            # If the element type is OAMEntryType, we can access its attributes
            if isinstance(list_type, OAMEntryType):
                attr_type = list_type.get_attribute_type(node.attribute)
                if attr_type is not None:
                    return attr_type
                else:
                    self.logger.error(f"Invalid OAM entry attribute: {node.attribute}")
                    raise UndeclaredVariableError(f"Invalid OAM entry attribute: {node.attribute}")

        # If the base object type has a get_attribute_type method
        if hasattr(base_obj, 'get_attribute_type'):
            attr_type = base_obj.get_attribute_type(node.attribute)
            if attr_type is not None:
                return attr_type
        
        # For attributes that aren't predefined, report an error
        self.logger.error(f"Undeclared attribute: {node.attribute} on object of type {base_obj}")
        raise UndeclaredVariableError(f"Undeclared attribute: {node.attribute} on object of type {base_obj}")
    
    def check_ProcedureCall(self, node: ProcedureCall) -> Type:
        """Type check a ProcedureCall node."""
        self.logger.info(f"Type checking procedure call: {node.name}")
        
        # Handle the case where the name is a Variable containing an AttributeAccess
        if hasattr(node.name, 'name') and hasattr(node.name.name, 'name') and hasattr(node.name.name, 'attribute'):
            # This handles: ProcedureCall(name=Variable(name=AttributeAccess(name='control', attribute='LCDon')))
            if isinstance(node.name.name.name, str):
                base = node.name.name.name
            else:
                base = node.name.name.name.name  # Get the actual string name
            attr = node.name.name.attribute
            proc_name = f"{base}.{attr}"
        # Handle simple attribute access
        elif hasattr(node.name, 'name') and hasattr(node.name, 'attribute'):
            # This handles: ProcedureCall(name=AttributeAccess(name='control', attribute='LCDon'))
            if isinstance(node.name.name, str):
                base = node.name.name
            elif hasattr(node.name.name, 'name'):
                base = node.name.name.name  # Get the actual string name
            else:
                base = str(node.name.name)
            attr = node.name.attribute
            proc_name = f"{base}.{attr}"
        # Handle simple Variable
        elif hasattr(node.name, 'name') and isinstance(node.name.name, str):
            proc_name = node.name.name
        # Handle string name
        elif isinstance(node.name, str):
            proc_name = node.name
        else:
            # Fallback case
            proc_name = str(node.name)
        
        # Check if the procedure has been declared
        if proc_name not in self.procedure_table:
            self.logger.error(f"Undeclared procedure: {proc_name}, Type: {type(node.name)}")
            raise UndeclaredVariableError(f"Undeclared procedure: {proc_name}")
    
        
        # Continue with the original implementation for argument checking
        param_types, return_type = self.procedure_table[proc_name]
        
        # Check if the number of arguments matches the number of parameters
        if len(node.args) != len(param_types):
            self.logger.error(f"Procedure '{proc_name}' expects {len(param_types)} arguments, got {len(node.args)}")
            raise TypeMismatchError(f"Procedure '{proc_name}' expects {len(param_types)} arguments, got {len(node.args)}")
        
        # Type check each argument
        for i, (arg, (_, param_type)) in enumerate(zip(node.args, param_types)):
            arg_type = self.check_node(arg)
            if arg_type != param_type:
                self.logger.error(f"Type mismatch in argument {i+1} of procedure '{proc_name}': expected {param_type}, got {arg_type}")
                raise TypeMismatchError(f"Type mismatch in argument {i+1} of procedure '{proc_name}': expected {param_type}, got {arg_type}")

        # Return the procedure's return type
        node.var_type = return_type
        return return_type
    
    def check_ProcedureDef(self, node: ProcedureDef) -> Type:
        """Type check a ProcedureDef node."""
        self.logger.info(f"Type checking procedure definition: {node.name}")
        
        # Check if the procedure has already been declared
        if node.name in self.procedure_table:
            raise DuplicateDeclarationError(f"Procedure '{node.name}' already declared")
        
        # Convert the return type string to a Type object
        return_type = self.string_to_type(node.return_type) if node.return_type else VoidType()
        
        # Save the previous return type (in case we're in a nested procedure)
        prev_return_type = self.current_return_type
        self.current_return_type = return_type
        
        # Create a new scope for the procedure's parameters
        old_symbol_table = self.symbol_table.copy()
        
        # Process the parameters
        param_types = []
        for param_name, param_type_str in node.params:
            param_type = self.string_to_type(param_type_str)
            param_types.append((param_name, param_type))
            
            # Add the parameter to the symbol table
            self.symbol_table[param_name] = param_type
        
        # Add the procedure to the procedure table
        self.procedure_table[node.name] = (param_types, return_type)
        
        # Type check the procedure body
        for statement in node.body:
            self.check_node(statement)
        
        # Restore the previous scope and return type
        self.symbol_table = old_symbol_table
        self.current_return_type = prev_return_type
        
        return VoidType()

# Usage example
def type_check(ast: ASTNode) -> None:
    """Type check an AST."""
    type_checker = TypeChecker()
    if isinstance(ast, Program):
        type_checker.check_program(ast)
    else:
        type_checker.check_node(ast)