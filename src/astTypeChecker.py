"""Type Checker for the Penguin Language

Traverses an AST and verifies type correctness according to language rules.
"""

# Stdlib imports
import os
import sys
from typing import List, Tuple, Union, Optional, Dict

# Extend module paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Custom modules
from src.astClasses import *
from src.astTypes import *
from src.predefinedVnF import initialize_hardware_elements
from src.customErrors import *
from src.logger import logger


# Start med at modtage det tree som vi har lavet i AST generator

# Vi skal også imens vi gennemløber, tjekke om typerne i procedure kald er OK, og om variablerne er defineret / erklæret. 
# Aka, liste over alle de forskellige variabler, lister, attributes (Gælder kun registers)
# Det samme gælder funktioner, men vi skal nok løbe dem igennem først, da funktionskald gerne skulle kunne placeres hvor end.

# Den skal nok køre et loop igennem de forskellige statements? Det giver ikke mening at lade tjekke om program er 
#   OK ud fra de forskellige statements, ikke engang alle statements behøver at blie tjekket
# Brug visitor pattern eller generic recursive function til at besøge alle noderne, 
# og fra bunden så finde den nuværende nodes typer, underliggende, på den vis at lade typen florere op

# I løbet af denne process, bliver semantikken tjekket om den er OK, 
# ift. godtagning af de forskellige nodes der tjekkes, efter alle childrens typer er gået op i træet

# Efter denne gennemløbning, kan vi returnere det samme træ som vi arbejdede på, da vi kun ændrer typerne på det.
# Kører det igennem uden fejl, er der ingen semantiske fejl, og det er nu et TAAST


# OKAY MERE KONKRET

# Gennemløb erklæringer / definitioner af variabler og funktioner, og tilføj dem til en liste der OGSÅ indeholder hardware registers
# Typetjek dem imens?


class TypeEnv: 
    # Symbol table for the type checker.
    def __init__(self):
        self.stack: List[Dict] = [{}]

    def push(self):
        self.stack.append({})

    def pop(self):
        self.stack.pop()

    def define(self, name, typ):
        self.stack[-1][name] = typ

    def lookup(self, name: str) -> Optional[Type]:
        for scope in reversed(self.stack):  # Check inner to outer
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
    
    def as_typeenv(self) -> TypeEnv:
        # Makes a new env for the procedure, with a copy of the current env
        env = TypeEnv()
        for name, (params, ret_type) in self.table.items():
            env.define(name, ProcedureType([typ for _, typ in params], ret_type)) # Er 
        return env


class TypeChecker:
    """Type checker for Penguin Language AST.
    
    Traverses an AST and verifies type and scope correctness according to language rules.
    """
    
    def __init__(self):
        
        self.env = TypeEnv() # Symbol table
        self.procedures = ProcedureEnv() # Procedure table
        self.current_return_type: Optional[Type] = None  # Return type of the current procedure
        
        # Initialize predefined hardware elements
        self._init_predefined_elements()
    
    def _init_predefined_elements(self):
        """Initialize predefined hardware modules, variables, and functions."""
        # Get predefined elements from the hardware module
        hardware_symbols, hardware_procedures = initialize_hardware_elements()
        
        # add to symboltable (env)
        for symbol, typ in hardware_symbols.items():
            self.env.define(symbol, typ)
        
        # Add procedures to the procedure table
        for name, (params, ret_type) in hardware_procedures.items():
            self.procedures.define(name, params, ret_type)
        
        logger.info(f"Initialized {len(hardware_symbols)} hardware symbols and {len(hardware_procedures)} hardware procedures")
    
    def string_to_type(self, type_str: str) -> Type:
        """Convert a type string to a Type object."""
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
        # Check if the type string is in the dictionary
        type_str = type_str.lower()
        if type_str in dictionary:
            return dictionary[type_str]
        else:
            # If not, handle the case where the type is not recognized
            logger.error(f"Invalid type: {type_str}")
            raise InvalidTypeError(f"Invalid type: {type_str} --- {type(type_str)}")
        
    def get_procedure_name(self, node: Union[ProcedureCall, ProcedureDef]) -> str:
        # hjælper methodf forr getting qa procedure namer, where the procedure might accessed with an attribute
        
        # node is usually a Variable or an AttributeAccess (possibly nested)
        # base case is when node is a string (the name of the procedure)
        if isinstance(node, str):
            return node
        # check if node is an AttributeAccess
        elif hasattr(node, 'name') and hasattr(node, 'attribute'):
            # recursively get the base name of each attribute, and add the attribute to the end
            base = self.get_procedure_name(node.name)
            return f"{base}.{node.attribute}"
        # check if node is a Variable
        elif hasattr(node, 'name'):
            # return the name of the node, which is the procedure name
            return self.get_procedure_name(node.name)
        # check if node is a Variable with a string name
        elif isinstance(node, Variable) and isinstance(node.name, str):
            return node.name
        # if nothign else, return the string representation of the node
        return str(node)  # fallback
    
    def check_node(self, node: ASTNode) -> Type:
        """Type check an AST node by dispatching to the appropriate method in the TypeChecker."""
        logger.debug(f"Type checking node: {type(node).__name__}")
        
        # Use a method dispatch pattern to call the appropriate check method
        method_name = f"check_{node.__class__.__name__}"
        method = getattr(self, method_name, None)
        
        if method is None:
            logger.error(f"No type checking method for {type(node).__name__}")
            raise TypeError(f"No type checking method for {type(node).__name__}")
        
        return method(node)
    
    def check_program(self, node: Program) -> None:
        """Type check a Program node."""
        logger.info("Type checking program")
        
        # Type check each statement in the program
        for stmt in node.statements:
            self.check_node(stmt)
    
    def check_Declaration(self, node: Declaration) -> None:
        """Type check a Declaration node."""
        logger.info(f"Type checking declaration: {node.name} of type {node.var_type}")
        
        # Check if the variable has already been declared in the current scope
        if self.env.lookup(node.name) is not None:
            if node.name in self.env.current_scope():
                raise DuplicateDeclarationError(f"Variable '{node.name}' already declared in this scope")
        
        # Convert the type string to a Type object
        var_type = self.string_to_type(node.var_type)
        
        # Add the variable to the symbol table, by defining it in the enviroment
        self.env.define(node.name, var_type)
        
        # Store type in the node for later use
        node.var_type = var_type

        logger.debug(f"Declared variable '{node.name}' with type {var_type}")
    
    def check_Assignment(self, node: Assignment) -> None:
        """Type check an Assignment node."""
        logger.info(f"Type checking assignment: {node.target}")
        
        # Type check the target and value
        target_type = self.check_node(node.target)
        value_type = self.check_node(node.value)
        
        # Store the type in the node for later use
        node.var_type = target_type
        
        # Check if the types match
        if target_type != value_type:   
            if (value_type == SpriteType() and target_type == IntType()):
                return 
            
            logger.error(f"Type mismatch in assignment: expected {target_type}, got {value_type}")
            raise TypeMismatchError(f"Type mismatch in assignment: expected {target_type}, got {value_type}")

        if isinstance(target_type, (TileMapType, TilesetType, SpriteType)):
            # Special case, where the above types cannot be reassigned at runtime
            logger.error(f"Cannot reassign {target_type} at runtime")
            raise TypeMismatchError(f"Cannot reassign {target_type} at runtime")
        
        logger.debug(f"Assigned {node.value} to {node.target}")

    def check_Initialization(self, node: Initialization) -> None:
        """Type check an Initialization node."""
        logger.info(f"Type checking initialization: {node.name} of type {node.var_type}")
        
        # Check if the variable is already declared in the current scope
        if self.env.lookup(node.name) is not None:
            if node.name in self.env.current_scope():
                raise DuplicateDeclarationError(f"Variable '{node.name}' already declared in this scope")
        
        # Convert the type string to a Type object
        var_type = self.string_to_type(node.var_type)
        
        # Add the variable to the symbol table
        self.env.define(node.name, var_type)
        
        # Type check the value
        value_type = self.check_node(node.value)
        
        # Store the type in the node for later use
        node.var_type = var_type
        
        # Check if the types match
        if var_type != value_type:
            # Special case for Tileset, TileMap, and Sprite which must be assigned strings
            if isinstance(var_type, (TilesetType, TileMapType, SpriteType)) and isinstance(value_type, StringType):
                return
            
            logger.error(f"Type mismatch in initialization: expected {var_type}, got {value_type}")
            raise TypeMismatchError(f"Type mismatch in initialization: expected {var_type}, got {value_type}")
    
    def check_ListInitialization(self, node: ListInitialization) -> None:
        """Type check a ListInitialization node."""
        logger.info(f"Type checking list initialization: {node.name}")
        
        # Check if the variable has already been declared in the current scope
        if self.env.lookup(node.name) is not None:
            if node.name in self.env.current_scope():
                raise DuplicateDeclarationError(f"Variable '{node.name}' already declared in this scope")
        
        # Per the rules, lists must always be of type int
        list_type = ListType(IntType())
        
        # Add the variable to the symbol table
        self.env.define(node.name, list_type)
        
        # Store the type in the node for later use
        node.var_type = list_type
        
        # Type check each value in the list
        for value in node.values:
            value_type = self.check_node(value)
            if value_type != IntType():
                logger.error(f"Type mismatch in list initialization: expected int, got {value_type}")
                raise TypeMismatchError(f"Type mismatch in list initialization: expected int, got {value_type}")
    
    def check_Conditional(self, node: Conditional) -> Type:
        """Type check a Conditional node."""
        logger.info("Type checking conditional statement")
        
        # Type check the condition
        condition_type = self.check_node(node.condition)
        
        # Check if the condition evaluates to a boolean (represented as int in this language)
        if not isinstance(condition_type, IntType):
            logger.error(f"Condition must be of type int, got {condition_type}")
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
        logger.info("Type checking loop")
        
        # Type check the condition
        condition_type = self.check_node(node.condition)
        
        # Check if the condition evaluates to a boolean (represented as int in this language)
        if not isinstance(condition_type, IntType):
            logger.error(f"Loop condition must be of type int, got {condition_type}")
            raise TypeMismatchError(f"Loop condition must be of type int, got {condition_type}")
        
        # Type check the body
        for statement in node.body:
            self.check_node(statement)
        
        return VoidType()
    
    def check_Return(self, node: Return) -> Type:
        """Type check a Return node."""
        logger.info("Type checking return statement")
        
        # Type check the return value
        value_type = self.check_node(node.value)
        
        # Store the type in the node for later use 
        node.var_type = value_type 
        
        # Check if the return type matches the current procedure's return type
        if self.current_return_type is None:
            logger.error("Return statement outside of procedure")
            raise TypeError("Return statement outside of procedure")
        
        if value_type != self.current_return_type:
            logger.error(f"Return type mismatch: expected {self.current_return_type}, got {value_type}")
            raise TypeMismatchError(f"Return type mismatch: expected {self.current_return_type}, got {value_type}")
    
        # Check if coid type, and if so if the value is None
        if isinstance(self.current_return_type, VoidType) and node.value is not None:
            logger.error("Void procedure should not return a value")
            raise TypeMismatchError("Void procedure should not return a value")
        
        return value_type
    
    def check_BinaryOp(self, node: BinaryOp) -> Type:
        """Type check a BinaryOp node."""
        logger.info(f"Type checking binary operation: {node.op}")
        
        # Type check the left and right operands
        left_type = self.check_node(node.left)
        right_type = self.check_node(node.right)
        
        # Store the type in the node for later use
        node.var_type = right_type
        
        # define sets of operators, taken from grammar
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
        
        # Check operator compatibility
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
        """Type check a UnaryOp node."""
        logger.info(f"Type checking unary operation: {node.op}")
        
        # Type check the operand
        operand_type = self.check_node(node.operand)
        
        # define sets of operators, taken from grammar
        arithmetic_operators = {'-', '+'}
        bitwise_operators = {'~'}
        logical_operators = {'not'}
        
        if node.op in arithmetic_operators | bitwise_operators | logical_operators:
            if not isinstance(operand_type, IntType):
                operator_type = "Arithmetic" if node.op in arithmetic_operators else \
                    "Bitwise" if node.op in bitwise_operators else \
                    "Logical"
                logger.error(f"{operator_type} operator '{node.op}' requires integer operand, got {operand_type}")
            node.var_type = IntType()  # Store the type in the node for later use
            return IntType()
        
        else:
            logger.error(f"Unknown unary operator: {node.op}")
            raise TypeError(f"Unknown unary operator: {node.op}")
    
    def check_IntegerLiteral(self, node: IntegerLiteral) -> Type:
        """Type check an IntegerLiteral node."""
        logger.debug(f"Integer literal: {node.value}")
        node.var_type = IntType()  # Store the type in the node for later use
        return IntType()
    
    def check_StringLiteral(self, node: StringLiteral) -> Type:
        """Type check a StringLiteral node."""
        logger.debug(f"String literal: {node.value}")
        node.var_type = StringType()  # Store the type in the node for later use
        return StringType()
    
    def check_Variable(self, node: Variable) -> Type:
        """Type check a Variable node."""
        logger.info(f"Type checking variable: {node.name}")
        
        # Handle the case where node.name is an AttributeAccess instance
        if isinstance(node.name, AttributeAccess):
            # When Variable contains an AttributeAccess, we should just check the AttributeAccess
            var_type = self.check_AttributeAccess(node.name)
            node.var_type = var_type
            return self.check_node(node.name)
        
        # Regular case - node.name is a string
        # Check if the variable has been declared
        var_type = self.env.lookup(node.name)
        if var_type is None:
            logger.error(f"Undeclared variable: {node.name}")
            raise UndeclaredVariableError(f"Undeclared variable: {node.name}")
        
        # Return the variable's type
        node.var_type = var_type
        return var_type
    
    def check_ListAccess(self, node: ListAccess) -> Type:
        """Type check a ListAccess node."""
        logger.info(f"Type checking list access: {node.name}")
        
        # Store the type in the node for later use
        node.var_type = IntType()
        
        base_type = None
        
        # Get the base object to check if it's indexable
        if isinstance(node.name, str):
            try:
                # Check if the variable has been declared, if not, raise an error, else get its type
                base_type = self.env.lookup(node.name)
            except KeyError:
                logger.error(f"Undeclared variable: {node.name}")
                raise UndeclaredVariableError(f"Undeclared variable: {node.name}")
        else:
            # If node.name is not a string, it's a nested structure (like a.b[0])
            base_type = self.check_node(node.name)
        
        # Check if the base object is indexable, like a list or array
        if not base_type.is_indexable():
            logger.error(f"Type {base_type} is not indexable")
            raise TypeMismatchError(f"Type {base_type} is not indexable")
        
        # Type check each index, ensuring they are of type int
        for index in node.indices:
            index_type = self.check_node(index)
            if not isinstance(index_type, IntType):
                logger.error(f"Index must be of type int, got {index_type}")
                raise TypeMismatchError(f"Index must be of type int, got {index_type}")
        
        # Return the type of element that we get when indexing this type, should be int
        return base_type.index_result_type()
    
    def check_AttributeAccess(self, node: AttributeAccess) -> Type:
        """Type check an AttributeAccess node."""
        
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
        """Type check a ProcedureCallStatement node."""
        logger.info("Type checking procedure call statement")
        
        # Type check the procedure call, siden det er en statement, så vi skal bare tjekke den
        self.check_node(node.call)
        
        return VoidType()
    
    def check_ProcedureCall(self, node: ProcedureCall) -> Type:
        """Type check a ProcedureCall node."""
        logger.info(f"Type checking procedure call: {node.name}")
        
        # get the procedure name
        proc_name = self.get_procedure_name(node)
        
        # get the procedure entry from the procedure table
        proc = self.procedures.lookup(proc_name)
        
        # check it against the procedure table
        if proc is None:
            logger.error(f"Undeclared procedure: {proc_name}")
            raise UndeclaredVariableError(f"Undeclared procedure: {proc_name}")

        # access the actual params given as input
        param_types, return_type = proc
        
        # Tjek om typer og parameternavne kan mappes
        if len(node.params) != len(param_types):
            logger.error(f"Procedure '{proc_name}' expects {len(param_types)} arguments, got {len(node.params)}")
            raise TypeMismatchError(f"Procedure '{proc_name}' expects {len(param_types)} arguments, got {len(node.params)}")
        
        # type check each of the actual arguments
        # loop over each argument and its corresponding parameter by index of a mapped tuple
        for i, (arg, (param_name, expected_type)) in enumerate(zip(node.params, param_types)):
            # check the type of the argument
            actual_type = self.check_node(arg)
            # see if the type of the argument matches the expected type from the procedure table
            if actual_type != expected_type:
                logger.error(f"Argument {i+1} ('{param_name}') of procedure '{proc_name}' has wrong type: expected {expected_type}, got {actual_type}")
                raise TypeMismatchError(f"Argument {i+1} ('{param_name}') of procedure '{proc_name}' has wrong type: expected {expected_type}, got {actual_type}")

        # Return the procedure's return type
        node.var_type = return_type
        return return_type
    
    def check_ProcedureDef(self, node: ProcedureDef) -> Type:
        """Type check a ProcedureDef node."""
        logger.info(f"Type checking procedure definition: {node.name}")
        
        # Check if the procedure has already been declared, dupilcate
        if self.procedures.lookup(node.name):
            logger.error(f"Duplicate procedure declaration: {node.name}")
            raise DuplicateDeclarationError(f"Procedure '{node.name}' already declared")
        
        # process formal parameters
        param_types = []
        for declaration in node.params: # params contains declarations of variables
            param_type = self.string_to_type(declaration.var_type)
            param_types.append((declaration.name, param_type))
        
        # process return type, of the procedure
        return_type = self.string_to_type(node.return_type) if node.return_type else VoidType()
        node.return_type = return_type
        
        # logger.debug(f"return_type: {node.return_type} --- {type(node.return_type)} --- {return_type} --- {type(return_type)}")
        
        # define the procedure in the procedure table
        self.procedures.define(node.name, param_types, return_type)
        
        # push a new scope for the procedure
        self.env.push()
        
        # define the parameters in the new scope
        for declaration in node.params:
            var_type = self.string_to_type(declaration.var_type)
            self.env.define(declaration.name, var_type)
            declaration.var_type = var_type
        
        # save the current return type and previous return type, if we are in a nested procedure
        previous_return_type = self.current_return_type
        self.current_return_type = return_type
        
        # check the body of the procedure
        for statement in node.body:
            self.check_node(statement)
            
        # return to the previous scope
        self.env.pop()
        
        # restore the previous return type
        self.current_return_type = previous_return_type
        
        return VoidType()


# Usage example
def type_check(ast: ASTNode) -> None:
    """Type check an AST."""
    type_checker = TypeChecker()
    if isinstance(ast, Program):
        type_checker.check_program(ast)
    else:
        type_checker.check_node(ast)
