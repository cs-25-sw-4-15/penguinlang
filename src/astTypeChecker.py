import os
import sys
from typing import List, Tuple, Union, Optional, Dict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.astClasses import *
from src.astTypes import *
from src.predefinedVnF import initialize_hardware_elements
from src.customErrors import *
from src.logger import logger



class TypeEnv: 
    def __init__(self):
        self.stack: List[Dict] = [{}]

    def push(self):
        self.stack.append({})

    def pop(self):
        self.stack.pop()

    def define(self, name, typ):
        self.stack[-1][name] = typ

    def lookup(self, name: str) -> Optional[Type]:
        for scope in reversed(self.stack): 
            if name in scope:
                return scope[name]
        return None

    def current_scope(self):
        return self.stack[-1]


class ProcedureEnv:
    def __init__(self):
        self.table: Dict[str, Tuple[List[Tuple[str, Type]], Type]] = {}

    def define(self, name: str, params: List[Tuple[str, Type]], return_type: Type):
        self.table[name] = (params, return_type)

    def lookup(self, name: str) -> Optional[Tuple[List[Tuple[str, Type]], Type]]:
        return self.table.get(name)


class TypeChecker:

    
    def __init__(self):
        
        self.env = TypeEnv() # Symbol table
        self.procedures = ProcedureEnv() # Procedure table
        self.current_return_type: Optional[Type] = None  # Return type of the current procedure
        
        self._init_predefined_elements()
    
    def _init_predefined_elements(self):

        hardware_symbols, hardware_procedures = initialize_hardware_elements()
        
        # add to symboltable (env)
        for symbol, typ in hardware_symbols.items():
            self.env.define(symbol, typ)
        
        # Add procedures to the procedure table
        for name, (params, ret_type) in hardware_procedures.items():
            self.procedures.define(name, params, ret_type)
        
        logger.info(f"Initialized {len(hardware_symbols)} hardware symbols and {len(hardware_procedures)} hardware procedures")
    
    def string_to_type(self, type_str: str) -> Type:
        logger.debug(f"Converting string '{type_str}' to type")
        
        dictionary = {
            "int": IntType(),
            "tileset": TilesetType(),
            "tilemap": TileMapType(),
            "sprite": SpriteType(),
            "string": StringType(),
            "void": VoidType(),
            "oamentry": OAMEntryType(),
            "list": ListType()
        }
        type_str = type_str.lower()
        if type_str in dictionary:
            return dictionary[type_str]
        else:
            logger.error(f"Invalid type: {type_str}")
            raise InvalidTypeError(f"Invalid type: {type_str} --- {type(type_str)}")
        
    def get_procedure_name(self, node: Union[ProcedureCall, ProcedureDef]) -> str:
        # hjælper methodf forr getting qa procedure namer, where the procedure might accessed with an attribute
        
        # node is usually a Variable or an AttributeAccess (possibly nested)
        if isinstance(node, str):
            return node
        elif hasattr(node, 'name') and hasattr(node, 'attribute'):
            base = self.get_procedure_name(node.name)
            return f"{base}.{node.attribute}"
        elif hasattr(node, 'name'):
            return self.get_procedure_name(node.name)
        elif isinstance(node, Variable) and isinstance(node.name, str):
            return node.name
        return str(node)  # fallback
    
    def check_node(self, node: ASTNode) -> Type:
        logger.debug(f"Type checking node: {type(node).__name__}")
        
        method_name = f"check_{node.__class__.__name__}"
        method = getattr(self, method_name, None)
        
        if method is None:
            logger.error(f"No type checking method for {type(node).__name__}")
            raise TypeError(f"No type checking method for {type(node).__name__}")
        
        return method(node)
    
    def check_program(self, node: Program) -> None:
        """Type check a Program node."""
        logger.info("Type checking program")
        
        for stmt in node.statements:
            self.check_node(stmt)
    
    def check_Declaration(self, node: Declaration) -> None:
        logger.info(f"Type checking declaration: {node.name} of type {node.var_type}")
        
        # Check if the variable has already been declared in the current scope
        if self.env.lookup(node.name) is not None:
            if node.name in self.env.current_scope():
                raise DuplicateDeclarationError(f"Variable '{node.name}' already declared in this scope")
        
        # Convert the type string to a Type object
        var_type = self.string_to_type(node.var_type)
        
        self.env.define(node.name, var_type)
        
        node.var_type = var_type

        logger.debug(f"Declared variable '{node.name}' with type {var_type}")
    
    def check_Assignment(self, node: Assignment) -> None:
        logger.info(f"Type checking assignment: {node.target}")
        
        target_type = self.check_node(node.target)
        value_type = self.check_node(node.value)
        
        node.var_type = target_type
        
        if target_type != value_type:   
            if (value_type == SpriteType() and target_type == IntType()):
                return 
            
            logger.error(f"Type mismatch in assignment: expected {target_type}, got {value_type}")
            raise TypeMismatchError(f"Type mismatch in assignment: expected {target_type}, got {value_type}")
        
        logger.debug(f"Assigned {node.value} to {node.target}")

    def check_Initialization(self, node: Initialization) -> None:
        logger.info(f"Type checking initialization: {node.name} of type {node.var_type}")
        
        if self.env.lookup(node.name) is not None:
            if node.name in self.env.current_scope():
                raise DuplicateDeclarationError(f"Variable '{node.name}' already declared in this scope")
        
        var_type = self.string_to_type(node.var_type)
        
        self.env.define(node.name, var_type)
        
        value_type = self.check_node(node.value)
        
        node.var_type = var_type
        
        if var_type != value_type:
            # Special case for Tileset, TileMap, and Sprite which must be assigned strings
            if isinstance(var_type, (TilesetType, TileMapType, SpriteType)) and isinstance(value_type, StringType):
                return
            
            logger.error(f"Type mismatch in initialization: expected {var_type}, got {value_type}")
            raise TypeMismatchError(f"Type mismatch in initialization: expected {var_type}, got {value_type}")
    
    def check_ListInitialization(self, node: ListInitialization) -> None:
        logger.info(f"Type checking list initialization: {node.name}")
        
        if self.env.lookup(node.name) is not None:
            if node.name in self.env.current_scope():
                raise DuplicateDeclarationError(f"Variable '{node.name}' already declared in this scope")
        
        list_type = ListType(IntType())
        
        self.env.define(node.name, list_type)
        
        node.var_type = list_type
        
        for value in node.values:
            value_type = self.check_node(value)
            if value_type != IntType():
                logger.error(f"Type mismatch in list initialization: expected int, got {value_type}")
                raise TypeMismatchError(f"Type mismatch in list initialization: expected int, got {value_type}")
    
    def check_Conditional(self, node: Conditional) -> Type:
        logger.info("Type checking conditional statement")
        
        condition_type = self.check_node(node.condition)
        
        if not isinstance(condition_type, IntType):
            logger.error(f"Condition must be of type int, got {condition_type}")
            raise TypeMismatchError(f"Condition must be of type int, got {condition_type}")
        
        for statement in node.then_body:
            self.check_node(statement)
        
        if node.else_body:
            for statement in node.else_body:
                self.check_node(statement)
        
        return VoidType()
    
    def check_Loop(self, node: Loop) -> Type:
        logger.info("Type checking loop")
        
        condition_type = self.check_node(node.condition)
        
        if not isinstance(condition_type, IntType):
            logger.error(f"Loop condition must be of type int, got {condition_type}")
            raise TypeMismatchError(f"Loop condition must be of type int, got {condition_type}")
        
        for statement in node.body:
            self.check_node(statement)
        
        return VoidType()
    
    def check_Return(self, node: Return) -> Type:
        logger.info("Type checking return statement")
        
        if(node.value):
            value_type = self.check_node(node.value)
        else:
            value_type = VoidType()
        
        node.var_type = value_type 
        
        if self.current_return_type is None:
            logger.error("Return statement outside of procedure")
            raise TypeError("Return statement outside of procedure")
        
        if value_type != self.current_return_type:
            logger.error(f"Return type mismatch: expected {self.current_return_type}, got {value_type}")
            raise TypeMismatchError(f"Return type mismatch: expected {self.current_return_type}, got {value_type}")
    
        if isinstance(self.current_return_type, VoidType) and node.value is not None:
            logger.error("Void procedure should not return a value")
            raise TypeMismatchError("Void procedure should not return a value")
        
        return value_type
    
    def check_BinaryOp(self, node: BinaryOp) -> Type:
        logger.info(f"Type checking binary operation: {node.op}")
        
        left_type = self.check_node(node.left)
        right_type = self.check_node(node.right)
        
        node.var_type = right_type
        
        complex_artimetic_operators = {'*'}
        simple_arithmetic_operators = {'+', '-'}
        bitwise_arthmetic_operators = {'<<', '>>'}
        x_than_operators = {'<', '>', '<=', '>='}
        equality_operators = {'==', '!='}
        bitwise_logical_operators1 = {'&'}
        bitwise_logical_operators2 = {'^'}
        bitwise_logical_operators3 = {'|'}
        logical_operators1 = {'and'}
        logical_operators2 = {'or'}
        
        if node.op in complex_artimetic_operators | simple_arithmetic_operators | bitwise_arthmetic_operators \
                                                  | x_than_operators | equality_operators | bitwise_logical_operators1 \
                                                  | bitwise_logical_operators2 | bitwise_logical_operators3 \
                                                  | logical_operators1 | logical_operators2:
                
            if not isinstance(left_type, IntType) or not isinstance(right_type, IntType):
                operator_type = "Arithmetic" if node.op in complex_artimetic_operators | simple_arithmetic_operators | bitwise_arthmetic_operators else \
                    "Comparison" if node.op in x_than_operators | equality_operators else \
                    "Bitwise" if node.op in bitwise_logical_operators1 | bitwise_logical_operators2 | bitwise_logical_operators3 else \
                    "Logical"
                logger.error(f"{operator_type} operator '{node.op}' requires integer operands, got {left_type} and {right_type}")
            return IntType()
        else:
            logger.error(f"Unknown binary operator: {node.op}")
            raise TypeError(f"Unknown binary operator: {node.op}")
    
    def check_UnaryOp(self, node: UnaryOp) -> Type:
        logger.info(f"Type checking unary operation: {node.op}")
        
        operand_type = self.check_node(node.operand)
        
        arithmetic_operators = {'-', '+'}
        bitwise_operators = {'~'}
        logical_operators = {'not'}
        
        if node.op in arithmetic_operators | bitwise_operators | logical_operators:
            if not isinstance(operand_type, IntType):
                operator_type = "Arithmetic" if node.op in arithmetic_operators else \
                    "Bitwise" if node.op in bitwise_operators else \
                    "Logical"
                logger.error(f"{operator_type} operator '{node.op}' requires integer operand, got {operand_type}")
            node.var_type = IntType()  
            return IntType()
        
        else:
            logger.error(f"Unknown unary operator: {node.op}")
            raise TypeError(f"Unknown unary operator: {node.op}")
    
    def check_IntegerLiteral(self, node: IntegerLiteral) -> Type:
        """Type check an IntegerLiteral node."""
        logger.debug(f"Integer literal: {node.value}")
        node.var_type = IntType() 
        return IntType()
    
    def check_StringLiteral(self, node: StringLiteral) -> Type:
        """Type check a StringLiteral node."""
        logger.debug(f"String literal: {node.value}")
        node.var_type = StringType() 
        return StringType()
    
    def check_Variable(self, node: Variable) -> Type:
        """Type check a Variable node."""
        logger.info(f"Type checking variable: {node.name}")
        
        if isinstance(node.name, AttributeAccess):
            var_type = self.check_AttributeAccess(node.name)
            node.var_type = var_type
            return self.check_node(node.name)
        
        var_type = self.env.lookup(node.name)
        if var_type is None:
            logger.error(f"Undeclared variable: {node.name}")
            raise UndeclaredVariableError(f"Undeclared variable: {node.name}")
        
        node.var_type = var_type
        return var_type
    
    def check_ListAccess(self, node: ListAccess) -> Type:
        logger.info(f"Type checking list access: {node.name}")
        
        node.var_type = IntType()
        
        base_type = None
        
        if isinstance(node.name, str):
            try:
                base_type = self.env.lookup(node.name)
            except KeyError:
                logger.error(f"Undeclared variable: {node.name}")
                raise UndeclaredVariableError(f"Undeclared variable: {node.name}")
        else:
            base_type = self.check_node(node.name)
        
        if not base_type.is_indexable():
            logger.error(f"Type {base_type} is not indexable")
            raise TypeMismatchError(f"Type {base_type} is not indexable")
        
        for index in node.indices:
            index_type = self.check_node(index)
            if not isinstance(index_type, IntType):
                logger.error(f"Index must be of type int, got {index_type}")
                raise TypeMismatchError(f"Index must be of type int, got {index_type}")
        
        return base_type.index_result_type()
    
    def check_AttributeAccess(self, node: AttributeAccess) -> Type:
        # TODO: Actually properly implement this
        # TODO: make less complex
        
        logger.info(f"Type checking attribute access: {node.attribute} on {node.name}")
        
        # Attributes can ahve complex paths, like a.b.c, so we need to handle that
        # to handle this we make the helper funcion that constructs the path
        def construct_path(name_path) -> str:
            # Check if name is a string
            if isinstance(name_path, str):
                return name_path
            # check if name is an AttributeAccess
            elif isinstance(name_path, AttributeAccess):
                # recursively construct the path
                return f"{construct_path(name_path.name)}.{name_path.attribute}"
            # check if name is a Variable
            elif hasattr(name_path, 'name'):
                return f"{name_path.name}.{node.attribute}"
            # else return the name as string
            else:
                return str(name_path)
        
        # Construct the full path
        base_name = construct_path(node.name)
        full_path = f"{base_name}.{node.attribute}"
        
        # Check is it is in the symbol table
        try:
            # Check if the variable has been declared
            var_type = self.env.lookup(full_path)
            return var_type
        except KeyError:
            # siden det så ikke er i symbol table, kan man tjekke videre
            pass
        
        # Get the base object type
        base_obj = self.check_node(node.name) if isinstance(node.name, ASTNode) else self.env.lookup(node.name) # self.symbol_table.get(node.name)
        
        if base_obj is None:
            logger.error(f"Undeclared variable: {node.name}")
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
                    logger.error(f"Invalid OAM entry attribute: {node.attribute}")
                    raise UndeclaredVariableError(f"Invalid OAM entry attribute: {node.attribute}")

        # If the base object type has a get_attribute_type method
        if hasattr(base_obj, 'get_attribute_type'):
            attr_type = base_obj.get_attribute_type(node.attribute)
            if attr_type is not None:
                return attr_type
        
        # For attributes that aren't predefined, report an error
        logger.error(f"Invalid attribute: {node.attribute} on object of type {base_obj}")
        raise InvalidAttributeError(f"Invalid attribute: {node.attribute} on object of type {base_obj}")
    
    def check_ProcedureCallStatement(self, node: ProcedureCallStatement) -> Type:
        logger.info("Type checking procedure call statement")
        
        self.check_node(node.call)
        
        return VoidType()
    
    def check_ProcedureCall(self, node: ProcedureCall) -> Type:
        logger.info(f"Type checking procedure call: {node.name}")
        
        proc_name = self.get_procedure_name(node)
        
        proc = self.procedures.lookup(proc_name)
        
        if proc is None:
            logger.error(f"Undeclared procedure: {proc_name}")
            raise UndeclaredVariableError(f"Undeclared procedure: {proc_name}")

        param_types, return_type = proc
        
        if len(node.params) != len(param_types):
            logger.error(f"Procedure '{proc_name}' expects {len(param_types)} arguments, got {len(node.params)}")
            raise TypeMismatchError(f"Procedure '{proc_name}' expects {len(param_types)} arguments, got {len(node.params)}")
        
        for i, (arg, (param_name, expected_type)) in enumerate(zip(node.params, param_types)):
            # check the type of the argument
            actual_type = self.check_node(arg)
            # see if the type of the argument matches the expected type from the procedure table
            if actual_type != expected_type:
                logger.error(f"Argument {i+1} ('{param_name}') of procedure '{proc_name}' has wrong type: expected {expected_type}, got {actual_type}")
                raise TypeMismatchError(f"Argument {i+1} ('{param_name}') of procedure '{proc_name}' has wrong type: expected {expected_type}, got {actual_type}")

        node.var_type = return_type
        return return_type
    
    def check_ProcedureDef(self, node: ProcedureDef) -> Type:
        logger.info(f"Type checking procedure definition: {node.name}")
        
        if self.procedures.lookup(node.name):
            logger.error(f"Duplicate procedure declaration: {node.name}")
            raise DuplicateDeclarationError(f"Procedure '{node.name}' already declared")
        
        param_types = []
        for declaration in node.params: # params contains declarations of variables
            param_type = self.string_to_type(declaration.var_type)
            param_types.append((declaration.name, param_type))
        
        return_type = self.string_to_type(node.return_type) if node.return_type else VoidType()
        node.return_type = return_type
        
        self.procedures.define(node.name, param_types, return_type)
        
        self.env.push()
        
        for declaration in node.params:
            var_type = self.string_to_type(declaration.var_type)
            self.env.define(declaration.name, var_type)
            declaration.var_type = var_type
        
        previous_return_type = self.current_return_type
        self.current_return_type = return_type
        
        for statement in node.body:
            self.check_node(statement)
            
        self.env.pop()
        
        self.current_return_type = previous_return_type
        
        return VoidType()


def type_check(ast: ASTNode) -> None:
    """Type check an AST."""
    type_checker = TypeChecker()
    if isinstance(ast, Program):
        type_checker.check_program(ast)
    else:
        type_checker.check_node(ast)
