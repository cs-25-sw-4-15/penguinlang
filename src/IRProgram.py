"""
Intermediate Representation (IR) Implementation for Penguin Language Compiler

This module transforms the type-annotated abstract syntax tree (TAAST) into
an intermediate representation (IR) that can be used for register allocation
and code generation.
"""

from typing import List, Dict, Optional, Union, Any, Set
from ast_classes import *
from asttypes import *

# IR Classes
class IRInstruction:
    """Base class for all IR instructions"""
    def __str__(self) -> str:
        return f"{self.__class__.__name__}"

class IRBinaryOp(IRInstruction):
    """Binary operation in IR"""
    def __init__(self, op: str, dest: str, left: str, right: str):
        self.op = op
        self.dest = dest
        self.left = left
        self.right = right
    
    def __str__(self) -> str:
        return f"{self.dest} = {self.left} {self.op} {self.right}"

class IRUnaryOp(IRInstruction):
    """Unary operation in IR"""
    def __init__(self, op: str, dest: str, operand: str):
        self.op = op
        self.dest = dest
        self.operand = operand
    
    def __str__(self) -> str:
        return f"{self.dest} = {self.op} {self.operand}"

class IRAssign(IRInstruction):
    """Assignment in IR"""
    def __init__(self, dest: str, src: str):
        self.dest = dest
        self.src = src
    
    def __str__(self) -> str:
        return f"{self.dest} = {self.src}"

class IRConstant(IRInstruction):
    """Constant assignment in IR"""
    def __init__(self, dest: str, value: Any):
        self.dest = dest
        self.value = value
    
    def __str__(self) -> str:
        return f"{self.dest} = {self.value}"

class IRLoad(IRInstruction):
    """Load from memory in IR"""
    def __init__(self, dest: str, addr: str):
        self.dest = dest
        self.addr = addr
    
    def __str__(self) -> str:
        return f"{self.dest} = load {self.addr}"

class IRStore(IRInstruction):
    """Store to memory in IR"""
    def __init__(self, addr: str, value: str):
        self.addr = addr
        self.value = value
    
    def __str__(self) -> str:
        return f"store {self.addr}, {self.value}"

class IRLabel(IRInstruction):
    """Label in IR"""
    def __init__(self, name: str):
        self.name = name
    
    def __str__(self) -> str:
        return f"{self.name}:"

class IRJump(IRInstruction):
    """Unconditional jump in IR"""
    def __init__(self, label: str):
        self.label = label
    
    def __str__(self) -> str:
        return f"jump {self.label}"

class IRCondJump(IRInstruction):
    """Conditional jump in IR"""
    def __init__(self, condition: str, true_label: str, false_label: Optional[str] = None):
        self.condition = condition
        self.true_label = true_label
        self.false_label = false_label
    
    def __str__(self) -> str:
        if self.false_label:
            return f"if {self.condition} jump {self.true_label} else jump {self.false_label}"
        return f"if {self.condition} jump {self.true_label}"

class IRCall(IRInstruction):
    """Procedure call in IR"""
    def __init__(self, proc_name: str, args: List[str], dest: Optional[str] = None):
        self.proc_name = proc_name
        self.args = args
        self.dest = dest
    
    def __str__(self) -> str:
        args_str = ", ".join(self.args)
        if self.dest:
            return f"{self.dest} = call {self.proc_name}({args_str})"
        return f"call {self.proc_name}({args_str})"

class IRReturn(IRInstruction):
    """Return instruction in IR"""
    def __init__(self, value: Optional[str] = None):
        self.value = value
    
    def __str__(self) -> str:
        if self.value:
            return f"return {self.value}"
        return "return"

class IRIndexedLoad(IRInstruction):
    """Load from indexed location in IR (for arrays/lists)"""
    def __init__(self, dest: str, base: str, index: str):
        self.dest = dest
        self.base = base
        self.index = index
    
    def __str__(self) -> str:
        return f"{self.dest} = {self.base}[{self.index}]"

class IRIndexedStore(IRInstruction):
    """Store to indexed location in IR (for arrays/lists)"""
    def __init__(self, base: str, index: str, value: str):
        self.base = base
        self.index = index
        self.value = value
    
    def __str__(self) -> str:
        return f"{self.base}[{self.index}] = {self.value}"

class IRHardwareRead(IRInstruction):
    """Read from a hardware register"""
    def __init__(self, dest: str, register: str):
        self.dest = dest
        self.register = register
    
    def __str__(self) -> str:
        return f"{self.dest} = hw_read({self.register})"

class IRHardwareWrite(IRInstruction):
    """Write to a hardware register"""
    def __init__(self, register: str, value: str):
        self.register = register
        self.value = value
    
    def __str__(self) -> str:
        return f"hw_write({self.register}, {self.value})"

class IRHardwareIndexedRead(IRInstruction):
    """Read from an indexed hardware register (like display.oam[i])"""
    def __init__(self, dest: str, register: str, index: str):
        self.dest = dest
        self.register = register
        self.index = index
    
    def __str__(self) -> str:
        return f"{self.dest} = hw_indexed_read({self.register}, {self.index})"

class IRHardwareIndexedWrite(IRInstruction):
    """Write to an indexed hardware register (like display.oam[i])"""
    def __init__(self, register: str, index: str, value: str):
        self.register = register
        self.index = index
        self.value = value
    
    def __str__(self) -> str:
        return f"hw_indexed_write({self.register}, {self.index}, {self.value})"

class IRHardwareCall(IRInstruction):

    """Call a hardware function (like control.LCDon())"""
    def __init__(self, module: str, function: str, args: List[str] = None):
        self.module = module
        self.function = function
        self.args = args or []
    
    def __str__(self) -> str:
        args_str = ", ".join(self.args)
        return f"hw_call({self.module}.{self.function}, [{args_str}])"

class IRHardwareMemCpy(IRInstruction):
    """Copy memory from one hardware register to another"""
    def __init__(self, dest: str, src: str, size: str):
        self.dest = dest
        self.src = src
        self.size = size
    
    def __str__(self) -> str:
        return f"hw_memcpy({self.dest}, {self.src}, {self.size})"

class IRProcedure:
    """Procedure in IR"""
    def __init__(self, name: str, params: List[str], return_type: Optional[Type] = None):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.instructions: List[IRInstruction] = []
    
    def add_instruction(self, instruction: IRInstruction) -> None:
        self.instructions.append(instruction)
    
    def __str__(self) -> str:
        params_str = ", ".join(self.params)
        ret_type = self.return_type if self.return_type else "void"
        header = f"procedure {self.name}({params_str}) -> {ret_type}:"
        body = "\n".join(f"  {instr}" for instr in self.instructions)
        return f"{header}\n{body}"

class IRProgram:
    """Complete IR program"""
    def __init__(self):
        self.procedures: Dict[str, IRProcedure] = {}
        self.globals: Dict[str, Type] = {}
        self.main_instructions: List[IRInstruction] = []
    
    def add_procedure(self, procedure: IRProcedure) -> None:
        self.procedures[procedure.name] = procedure
    
    def add_global(self, name: str, type_: Type) -> None:
        self.globals[name] = type_
    
    def add_main_instruction(self, instruction: IRInstruction) -> None:
        self.main_instructions.append(instruction)
    
    def __str__(self) -> str:
        globals_str = "\n".join(f"global {name}: {type_}" for name, type_ in self.globals.items())
        main_str = "\n".join(f"{instr}" for instr in self.main_instructions)
        procedures_str = "\n\n".join(str(proc) for proc in self.procedures.values())
        
        result = []
        if globals_str:
            result.append("// Globals")
            result.append(globals_str)
            result.append("")
        
        if main_str:
            result.append("// Main")
            result.append(main_str)
            result.append("")
        
        if procedures_str:
            result.append("// Procedures")
            result.append(procedures_str)
        
        return "\n".join(result)

class IRGenerator:
    """Generates IR from a type-annotated AST"""
    
    def __init__(self):
        self.program = IRProgram()
        self.current_procedure: Optional[IRProcedure] = None
        self.temp_counter = 0
        self.label_counter = 0
        
        # Initialize hardware registers
        self.hardware_registers = set()
        self.initialize_hardware_registers()
    
    def new_temp(self) -> str:
        """Generate a new temporary variable name"""
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp
    
    def new_label(self) -> str:
        """Generate a new label name"""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label
    
    def add_instruction(self, instruction: IRInstruction) -> None:
        """Add an instruction to the current procedure or main section"""
        if self.current_procedure:
            self.current_procedure.add_instruction(instruction)
        else:
            self.program.add_main_instruction(instruction)
    
    def generate(self, ast: Program) -> IRProgram:
        """Generate IR from an AST"""
        # First collect global variables and procedures
        for statement in ast.statements:
            if isinstance(statement, ProcedureDef):
                # Just register the procedure signature first
                params = [param[1] for param in statement.params]  # Extract parameter names
                return_type = None
                if statement.return_type and statement.return_type != "void":
                    return_type = self.string_to_type(statement.return_type)
                
                procedure = IRProcedure(statement.name, params, return_type)
                self.program.add_procedure(procedure)
            elif isinstance(statement, (Declaration, Initialization)):
                # Register globals
                type_ = None
                if isinstance(statement, Declaration):
                    type_ = self.string_to_type(statement.var_type)
                    self.program.add_global(statement.name, type_)
                else:  # Initialization
                    type_ = self.string_to_type(statement.var_type)
                    self.program.add_global(statement.name, type_)
        
        # Now generate code for all statements
        for statement in ast.statements:
            if isinstance(statement, ProcedureDef):
                # Now generate the procedure body
                procedure = self.program.procedures[statement.name]
                self.current_procedure = procedure
                for stmt in statement.body:
                    self.visit(stmt)
                self.current_procedure = None
            else:
                # Generate code for global initialization and other top-level statements
                self.visit(statement)
        
        return self.program
    
    def initialize_hardware_registers(self):
        """Initialize the set of hardware registers"""
        # Display subsystem registers
        self.hardware_registers.add("display_tileset0")
        self.hardware_registers.add("display_tilemap0")
        
        # OAM (Object Attribute Memory) registers
        # This is handled as a special case for array/list-like access
        self.hardware_registers.add("display_oam")
        
        # Input state registers
        self.hardware_registers.add("input_Right")
        self.hardware_registers.add("input_Left")
        self.hardware_registers.add("input_Up")
        self.hardware_registers.add("input_Down")
        self.hardware_registers.add("input_A")
        self.hardware_registers.add("input_B")
        self.hardware_registers.add("input_Start")
        self.hardware_registers.add("input_Select")
    
    def is_hardware_register(self, name: str) -> bool:
        """Check if a name refers to a hardware register"""
        return name in self.hardware_registers
    
    def string_to_type(self, type_str: Union[str, Type]) -> Type:
        """Convert a type string to a Type object"""
        if isinstance(type_str, Type):
            return type_str
            
        if type_str == "int":
            return IntType()
        elif type_str == "tileset":
            return TilesetType()
        elif type_str == "tilemap":
            return TileMapType()
        elif type_str == "sprite":
            return SpriteType()
        elif type_str == "void":
            return VoidType()
        else:
            raise ValueError(f"Unknown type: {type_str}")
    
    def visit(self, node: ASTNode) -> Optional[str]:
        """Visit an AST node and generate IR instructions"""
        method_name = f"visit_{node.__class__.__name__}"
        method = getattr(self, method_name, None)
        
        if method is None:
            raise NotImplementedError(f"IR generation not implemented for {node.__class__.__name__}")
        
        return method(node)
    
    # Visit methods for different AST node types
    
    def visit_Program(self, node: Program) -> None:
        """Visit a Program node"""
        for statement in node.statements:
            self.visit(statement)
    
    def visit_Declaration(self, node: Declaration) -> None:
        """Visit a Declaration node"""
        # For declarations, we don't need to generate IR code
        # unless it's a local variable in a procedure
        if self.current_procedure:
            # Add local variable initialization if inside a procedure
            pass
    
    def visit_Assignment(self, node: Assignment) -> None:
        """Visit an Assignment node"""
        value_temp = self.visit(node.value)
        
        if isinstance(node.target, Variable):
            # Simple variable assignment
            target_name = node.target.name
            if self.is_hardware_register(target_name):
                # Writing to a hardware register
                self.add_instruction(IRHardwareWrite(target_name, value_temp))
            else:
                # Normal variable assignment
                self.add_instruction(IRAssign(target_name, value_temp))
        elif isinstance(node.target, ListAccess):
            # List/array assignment
            base_name = node.target.name
            if isinstance(base_name, Variable):
                base_name = base_name.name
            
            # Calculate the index
            index_temp = self.visit(node.target.indices[0])  # Assuming single index for now
            
            # Check if this is a hardware register array
            if base_name == "display.oam" or self.is_hardware_register(base_name):
                # Hardware indexed write
                self.add_instruction(IRHardwareIndexedWrite(base_name, index_temp, value_temp))
            else:
                # Normal indexed store
                self.add_instruction(IRIndexedStore(base_name, index_temp, value_temp))
        elif isinstance(node.target, AttributeAccess):
            # Handle attribute access (for OAM entries, etc.)
            base_name = node.target.name
            if isinstance(base_name, Variable):
                base_name = base_name.name
            
            full_name = f"{base_name}.{node.target.attribute}"
            
            # Check if this is a hardware register
            if self.is_hardware_register(full_name) or base_name == "display.oam":
                # Hardware register write
                self.add_instruction(IRHardwareWrite(full_name, value_temp))
            else:
                # Normal attribute store
                self.add_instruction(IRStore(full_name, value_temp))
    
    def visit_Initialization(self, node: Initialization) -> None:
        """Visit an Initialization node"""
        value_temp = self.visit(node.value)
        
        # If in a procedure, generate assignment; otherwise, it's a global initialization
        if self.current_procedure:
            self.add_instruction(IRAssign(node.name, value_temp))
        else:
            # For global initializations, add to main section
            self.add_instruction(IRAssign(node.name, value_temp))
    
    def visit_ListInitialization(self, node: ListInitialization) -> None:
        """Visit a ListInitialization node"""
        # Initialize each element of the list
        for i, value in enumerate(node.values):
            value_temp = self.visit(value)
            self.add_instruction(IRIndexedStore(node.name, str(i), value_temp))
    
    def visit_Conditional(self, node: Conditional) -> None:
        """Visit a Conditional node"""
        condition_temp = self.visit(node.condition)
        
        true_label = self.new_label()
        end_label = self.new_label()
        
        if node.else_body:
            false_label = self.new_label()
            # Jump to false_label if condition is false
            self.add_instruction(IRCondJump(condition_temp, true_label, false_label))
            
            # True branch
            self.add_instruction(IRLabel(true_label))
            for stmt in node.then_body:
                self.visit(stmt)
            self.add_instruction(IRJump(end_label))
            
            # False branch
            self.add_instruction(IRLabel(false_label))
            for stmt in node.else_body:
                self.visit(stmt)
            
            # End of conditional
            self.add_instruction(IRLabel(end_label))
        else:
            # Jump to end_label if condition is false
            self.add_instruction(IRCondJump(condition_temp, true_label))
            
            # True branch (executed only if condition is true)
            self.add_instruction(IRLabel(true_label))
            for stmt in node.then_body:
                self.visit(stmt)
            
            # End of conditional
            self.add_instruction(IRLabel(end_label))
    
    def visit_Loop(self, node: Loop) -> None:
        """Visit a Loop node"""
        start_label = self.new_label()
        body_label = self.new_label()
        end_label = self.new_label()
        
        # Start of loop
        self.add_instruction(IRLabel(start_label))
        
        # Evaluate condition
        condition_temp = self.visit(node.condition)
        
        # If condition is true, jump to body; otherwise, exit loop
        self.add_instruction(IRCondJump(condition_temp, body_label, end_label))
        
        # Loop body
        self.add_instruction(IRLabel(body_label))
        for stmt in node.body:
            self.visit(stmt)
        
        # Jump back to start for next iteration
        self.add_instruction(IRJump(start_label))
        
        # End of loop
        self.add_instruction(IRLabel(end_label))
    
    def visit_Return(self, node: Return) -> None:
        """Visit a Return node"""
        if node.value:
            value_temp = self.visit(node.value)
            self.add_instruction(IRReturn(value_temp))
        else:
            self.add_instruction(IRReturn())
    
    def visit_ProcedureCallStatement(self, node: ProcedureCallStatement) -> None:
        """Visit a ProcedureCallStatement node"""
        self.visit(node.call)  # Just delegate to visit_ProcedureCall
    
    def visit_BinaryOp(self, node: BinaryOp) -> str:
        """Visit a BinaryOp node and return the temp var holding the result"""
        left_temp = self.visit(node.left)
        right_temp = self.visit(node.right)
        
        result_temp = self.new_temp()
        self.add_instruction(IRBinaryOp(node.op, result_temp, left_temp, right_temp))
        
        return result_temp
    
    def visit_UnaryOp(self, node: UnaryOp) -> str:
        """Visit a UnaryOp node and return the temp var holding the result"""
        operand_temp = self.visit(node.operand)
        
        result_temp = self.new_temp()
        self.add_instruction(IRUnaryOp(node.op, result_temp, operand_temp))
        
        return result_temp
    
    def visit_IntegerLiteral(self, node: IntegerLiteral) -> str:
        """Visit an IntegerLiteral node and return the temp var holding the value"""
        result_temp = self.new_temp()
        self.add_instruction(IRConstant(result_temp, node.value))
        
        return result_temp
    
    def visit_StringLiteral(self, node: StringLiteral) -> str:
        """Visit a StringLiteral node and return the temp var holding the value"""
        result_temp = self.new_temp()
        self.add_instruction(IRConstant(result_temp, node.value))
        
        return result_temp
    
    def visit_Variable(self, node: Variable) -> str:
        """Visit a Variable node and return the variable name or a temp var for hardware registers"""
        if isinstance(node.name, str):
            var_name = node.name
            
            # Handle hardware registers
            if self.is_hardware_register(var_name):
                result_temp = self.new_temp()
                self.add_instruction(IRHardwareRead(result_temp, var_name))
                return result_temp
            
            # Regular variable
            return var_name
        else:
            # Handle case where Variable contains an object (e.g., AttributeAccess)
            return self.visit(node.name)
    
    def visit_ListAccess(self, node: ListAccess) -> str:
        """Visit a ListAccess node and return the temp var holding the accessed value"""
        base_name = node.name
        if isinstance(base_name, Variable):
            base_name = base_name.name
        
        # Calculate the index
        index_temp = self.visit(node.indices[0])  # Assuming single index for now
        
        result_temp = self.new_temp()
        
        # Check if this is a hardware register array
        if base_name == "display.oam" or self.is_hardware_register(base_name):
            # Hardware indexed read
            self.add_instruction(IRHardwareIndexedRead(result_temp, base_name, index_temp))
        else:
            # Normal indexed load
            self.add_instruction(IRIndexedLoad(result_temp, base_name, index_temp))
        
        return result_temp
    
    def visit_AttributeAccess(self, node: AttributeAccess) -> str:
        """Visit an AttributeAccess node and return the temp var holding the accessed value"""
        base_name = node.name
        if isinstance(base_name, Variable):
            base_name = base_name.name
        
        full_name = f"{base_name}.{node.attribute}"
        result_temp = self.new_temp()
        
        # Check if this is a hardware module function call (like control.LCDon)
        if base_name == "control" and node.attribute in ["LCDon", "LCDoff", "waitVBlank", "updateInput"]:
            # This is not an attribute access but a procedure call without parameters
            # Will be handled by visit_ProcedureCall
            pass
        # Check if this is a hardware register
        elif self.is_hardware_register(full_name) or base_name == "display.oam":
            # Hardware register read
            self.add_instruction(IRHardwareRead(result_temp, full_name))
        else:
            # Normal attribute load
            self.add_instruction(IRLoad(result_temp, full_name))
        
        return result_temp
    
    def visit_ProcedureCall(self, node: ProcedureCall) -> Optional[str]:
        """Visit a ProcedureCall node and return the temp var holding the result (if any)"""
        # Evaluate arguments
        arg_temps = []
        for arg in node.args:
            arg_temp = self.visit(arg)
            arg_temps.append(arg_temp)
        
        # Get procedure name
        proc_name = node.name
        
        # Handle case where proc_name is an AttributeAccess (like control.LCDon)
        if isinstance(proc_name, AttributeAccess):
            module_name = proc_name.name
            if isinstance(module_name, Variable):
                module_name = module_name.name
            
            function_name = proc_name.attribute
            
            # Special case for hardware functions
            if module_name == "control" and function_name in ["LCDon", "LCDoff", "waitVBlank", "updateInput"]:
                self.add_instruction(IRHardwareCall(module_name, function_name, arg_temps))
                return None  # These functions don't return a value
            
            # Construct the full name for regular procedure lookup
            proc_name = f"{module_name}.{function_name}"
        
        elif isinstance(proc_name, Variable):
            proc_name = proc_name.name
        
        # Check if procedure has a return value
        # For simplicity, assuming anything other than void returns a value
        procedure = self.program.procedures.get(proc_name)
        has_return = procedure and procedure.return_type and not isinstance(procedure.return_type, VoidType)
        
        if has_return:
            result_temp = self.new_temp()
            self.add_instruction(IRCall(proc_name, arg_temps, result_temp))
            return result_temp
        else:
            self.add_instruction(IRCall(proc_name, arg_temps))
            return None