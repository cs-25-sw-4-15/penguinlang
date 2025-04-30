"""
Intermediate Representation (IR) for the Penguin compiler.

This module takes a type-annotated AST and generates a linear IR suitable for
register allocation and code generation for the Game Boy target.
"""

from typing import List, Dict, Set, Tuple, Optional, Union
from ast_classes import *
from asttypes import *

# Each IR instruction has a simple format: dest = src1 op src2
# For operations without a destination (like jumps), dest can be None
class IRInstruction:
    """Base class for all IR instructions."""
    def __init__(self):
        self.next_instruction = None  # For control flow graph

    def get_uses(self) -> Set[str]:
        """Get set of variables used by this instruction."""
        return set()
    
    def get_defs(self) -> Set[str]:
        """Get set of variables defined by this instruction."""
        return set()

    def __str__(self) -> str:
        """String representation of the instruction."""
        return "IR_INSTRUCTION"

class IRAssign(IRInstruction):
    """Assignment instruction: dest = src"""
    def __init__(self, dest: str, src: str):
        super().__init__()
        self.dest = dest
        self.src = src
    
    def get_uses(self) -> Set[str]:
        return {self.src}
    
    def get_defs(self) -> Set[str]:
        return {self.dest}

    def __str__(self) -> str:
        return f"{self.dest} = {self.src}"

class IRBinary(IRInstruction):
    """Binary operation: dest = left op right"""
    def __init__(self, dest: str, left: str, op: str, right: str):
        super().__init__()
        self.dest = dest
        self.left = left
        self.op = op
        self.right = right
    
    def get_uses(self) -> Set[str]:
        return {self.left, self.right}
    
    def get_defs(self) -> Set[str]:
        return {self.dest}

    def __str__(self) -> str:
        return f"{self.dest} = {self.left} {self.op} {self.right}"

class IRUnary(IRInstruction):
    """Unary operation: dest = op src"""
    def __init__(self, dest: str, op: str, src: str):
        super().__init__()
        self.dest = dest
        self.op = op
        self.src = src
    
    def get_uses(self) -> Set[str]:
        return {self.src}
    
    def get_defs(self) -> Set[str]:
        return {self.dest}

    def __str__(self) -> str:
        return f"{self.dest} = {self.op} {self.src}"

class IRConstant(IRInstruction):
    """Load constant: dest = constant"""
    def __init__(self, dest: str, value: Union[int, str]):
        super().__init__()
        self.dest = dest
        self.value = value
    
    def get_defs(self) -> Set[str]:
        return {self.dest}

    def __str__(self) -> str:
        return f"{self.dest} = {self.value}"

class IRLabel(IRInstruction):
    """Label for jumps"""
    def __init__(self, label: str):
        super().__init__()
        self.label = label

    def __str__(self) -> str:
        return f"{self.label}:"

class IRJump(IRInstruction):
    """Unconditional jump: goto label"""
    def __init__(self, label: str):
        super().__init__()
        self.label = label

    def __str__(self) -> str:
        return f"goto {self.label}"

class IRCondJump(IRInstruction):
    """Conditional jump: if condition goto label"""
    def __init__(self, condition: str, label: str):
        super().__init__()
        self.condition = condition
        self.label = label
    
    def get_uses(self) -> Set[str]:
        return {self.condition}

    def __str__(self) -> str:
        return f"if {self.condition} goto {self.label}"

class IRReturn(IRInstruction):
    """Return value: return value"""
    def __init__(self, value: Optional[str] = None):
        super().__init__()
        self.value = value
    
    def get_uses(self) -> Set[str]:
        return {self.value} if self.value else set()

    def __str__(self) -> str:
        if self.value:
            return f"return {self.value}"
        return "return"

class IRCall(IRInstruction):
    """Function call: dest = call func(args)"""
    def __init__(self, dest: Optional[str], func: str, args: List[str]):
        super().__init__()
        self.dest = dest
        self.func = func
        self.args = args
    
    def get_uses(self) -> Set[str]:
        return set(self.args)
    
    def get_defs(self) -> Set[str]:
        return {self.dest} if self.dest else set()

    def __str__(self) -> str:
        args_str = ", ".join(self.args)
        if self.dest:
            return f"{self.dest} = call {self.func}({args_str})"
        return f"call {self.func}({args_str})"

class IRArrayStore(IRInstruction):
    """Array store: array[index] = value"""
    def __init__(self, array: str, index: str, value: str):
        super().__init__()
        self.array = array
        self.index = index
        self.value = value
    
    def get_uses(self) -> Set[str]:
        return {self.array, self.index, self.value}

    def __str__(self) -> str:
        return f"{self.array}[{self.index}] = {self.value}"

class IRArrayLoad(IRInstruction):
    """Array load: dest = array[index]"""
    def __init__(self, dest: str, array: str, index: str):
        super().__init__()
        self.dest = dest
        self.array = array
        self.index = index
    
    def get_uses(self) -> Set[str]:
        return {self.array, self.index}
    
    def get_defs(self) -> Set[str]:
        return {self.dest}

    def __str__(self) -> str:
        return f"{self.dest} = {self.array}[{self.index}]"

class IRFunction:
    """A function in the IR."""
    def __init__(self, name: str, params: List[str], locals: Dict[str, Type]):
        self.name = name
        self.params = params
        self.locals = locals
        self.instructions: List[IRInstruction] = []
    
    def add_instruction(self, instr: IRInstruction):
        """Add an instruction to the function."""
        self.instructions.append(instr)

    def __str__(self) -> str:
        result = f"function {self.name}({', '.join(self.params)}) {{\n"
        for instr in self.instructions:
            result += f"  {instr}\n"
        result += "}\n"
        return result

class IRProgram:
    """The entire program in IR form."""
    def __init__(self):
        self.globals: Dict[str, Type] = {}
        self.functions: Dict[str, IRFunction] = {}
        self.string_literals: Dict[str, str] = {}  # Maps string literals to unique labels
        self.temp_counter = 0
        self.label_counter = 0
    
    def add_function(self, func: IRFunction):
        """Add a function to the program."""
        self.functions[func.name] = func
    
    def add_global(self, name: str, type_: Type):
        """Add a global variable to the program."""
        self.globals[name] = type_
    
    def new_temp(self) -> str:
        """Generate a new temporary variable name."""
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp
    
    def new_label(self) -> str:
        """Generate a new label name."""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label
    
    def add_string_literal(self, value: str) -> str:
        """Add a string literal to the program and return its label."""
        if value in self.string_literals:
            return self.string_literals[value]
        
        label = f"str{len(self.string_literals)}"
        self.string_literals[value] = label
        return label
    
    def __str__(self) -> str:
        result = "// IR Program\n\n"
        
        # Print globals
        result += "// Globals\n"
        for name, type_ in self.globals.items():
            result += f"global {name}: {type_}\n"
        result += "\n"
        
        # Print string literals
        result += "// String Literals\n"
        for value, label in self.string_literals.items():
            result += f"{label}: \"{value}\"\n"
        result += "\n"
        
        # Print functions
        for func in self.functions.values():
            result += str(func) + "\n"
        
        return result

class IRGenerator:
    """Generates IR from a type-annotated AST."""
    def __init__(self):
        self.program = IRProgram()
        self.current_function = None
        self.continue_labels = []
        self.break_labels = []
        self.predefined_hardware = self._get_predefined_hardware()
    
    def _get_predefined_hardware(self) -> Set[str]:
        """Get a set of predefined hardware identifiers."""
        # Based on your PredefinedFsAndVs.py
        return {
            "display.tileset0", "display.tilemap0", "display.oam",
            "control.LCDon", "control.LCDoff", "control.waitVBlank", "control.updateInput",
            "input.Right", "input.Left", "input.Up", "input.Down",
            "input.A", "input.B", "input.Start", "input.Select"
        }
    
    def generate(self, ast: Program) -> IRProgram:
        """Generate IR from an AST."""
        # First pass: collect all global variables and procedures
        self._collect_globals_and_procedures(ast)
        
        # Second pass: generate IR for each procedure
        self._generate_procedures(ast)
        
        return self.program
    
    def _collect_globals_and_procedures(self, ast: Program):
        """First pass: collect all global variables and procedures."""
        for stmt in ast.statements:
            if isinstance(stmt, Declaration):
                self.program.add_global(stmt.name, stmt.var_type)
            elif isinstance(stmt, Initialization):
                self.program.add_global(stmt.name, stmt.var_type)
            elif isinstance(stmt, ProcedureDef):
                # Create function entry but don't populate it yet
                params = [name for _, name in stmt.params]
                locals = {}
                func = IRFunction(stmt.name, params, locals)
                self.program.add_function(func)
    
    def _generate_procedures(self, ast: Program):
        """Second pass: generate IR for each procedure."""
        for stmt in ast.statements:
            if isinstance(stmt, ProcedureDef):
                self._generate_procedure(stmt)
            elif isinstance(stmt, (Declaration, Initialization)):
                # These are handled in first pass
                pass
            else:
                # Global statements outside procedures
                # Create a "main" procedure if it doesn't exist
                if "main" not in self.program.functions:
                    self.program.add_function(IRFunction("main", [], {}))
                
                # Set current function to main
                self.current_function = self.program.functions["main"]
                
                # Generate IR for the statement
                self._generate_statement(stmt)
    
    def _generate_procedure(self, proc: ProcedureDef):
        """Generate IR for a procedure."""
        func = self.program.functions[proc.name]
        self.current_function = func
        
        # Add parameters to locals
        for param_type, param_name in proc.params:
            func.locals[param_name] = param_type
        
        # Generate IR for each statement in the procedure
        for stmt in proc.body:
            self._generate_statement(stmt)
        
        # Add implicit return for void procedures
        if proc.return_type is None or proc.return_type == VoidType():
            func.add_instruction(IRReturn())
    
    def _generate_statement(self, stmt: ASTNode):
        """Generate IR for a statement."""
        if isinstance(stmt, Declaration):
            self._generate_declaration(stmt)
        elif isinstance(stmt, Assignment):
            self._generate_assignment(stmt)
        elif isinstance(stmt, Initialization):
            self._generate_initialization(stmt)
        elif isinstance(stmt, ListInitialization):
            self._generate_list_initialization(stmt)
        elif isinstance(stmt, Conditional):
            self._generate_conditional(stmt)
        elif isinstance(stmt, Loop):
            self._generate_loop(stmt)
        elif isinstance(stmt, Return):
            self._generate_return(stmt)
        elif isinstance(stmt, ProcedureCallStatement):
            self._generate_procedure_call_statement(stmt)
        else:
            raise ValueError(f"Unsupported statement type: {type(stmt)}")
    
    def _generate_declaration(self, decl: Declaration):
        """Generate IR for a variable declaration."""
        # Add to locals if we're in a function
        if self.current_function:
            self.current_function.locals[decl.name] = decl.var_type
    
    def _generate_initialization(self, init: Initialization):
        """Generate IR for a variable initialization."""
        # Add to locals if we're in a function
        if self.current_function:
            self.current_function.locals[init.name] = init.var_type
        
        # Generate the value
        value_temp = self._generate_expression(init.value)
        
        # Assign to variable
        if self.current_function:
            self.current_function.add_instruction(IRAssign(init.name, value_temp))
    
    def _generate_list_initialization(self, init: ListInitialization):
        """Generate IR for a list initialization."""
        # Add to locals if we're in a function
        if self.current_function:
            self.current_function.locals[init.name] = ListType(IntType())
        
        # For each value in the list, assign it to array[index]
        for i, value in enumerate(init.values):
            value_temp = self._generate_expression(value)
            index_temp = self.program.new_temp()
            self.current_function.add_instruction(IRConstant(index_temp, i))
            self.current_function.add_instruction(IRArrayStore(init.name, index_temp, value_temp))
    
    def _generate_assignment(self, assign: Assignment):
        """Generate IR for an assignment."""
        # Generate the value
        value_temp = self._generate_expression(assign.value)
        
        # Handle different target types
        if isinstance(assign.target, Variable):
            self.current_function.add_instruction(IRAssign(assign.target.name, value_temp))
        elif isinstance(assign.target, ListAccess):
            array_name = assign.target.name
            if len(assign.target.indices) != 1:
                raise ValueError("Multi-dimensional arrays not supported yet")
            
            index_temp = self._generate_expression(assign.target.indices[0])
            self.current_function.add_instruction(IRArrayStore(array_name, index_temp, value_temp))
        elif isinstance(assign.target, AttributeAccess):
            # Handle attribute access, which is usually hardware-related in Penguin
            full_name = f"{assign.target.name}.{assign.target.attribute}"
            self.current_function.add_instruction(IRAssign(full_name, value_temp))
        else:
            raise ValueError(f"Unsupported assignment target: {type(assign.target)}")
    
    def _generate_conditional(self, cond: Conditional):
        """Generate IR for an if/else statement."""
        condition_temp = self._generate_expression(cond.condition)
        
        else_label = self.program.new_label()
        end_label = self.program.new_label()
        
        # If condition is false, goto else
        self.current_function.add_instruction(IRCondJump(condition_temp, else_label))
        
        # Generate then body
        for stmt in cond.then_body:
            self._generate_statement(stmt)
        
        # At end of then body, goto end
        self.current_function.add_instruction(IRJump(end_label))
        
        # Else label
        self.current_function.add_instruction(IRLabel(else_label))
        
        # Generate else body if it exists
        if cond.else_body:
            for stmt in cond.else_body:
                self._generate_statement(stmt)
        
        # End label
        self.current_function.add_instruction(IRLabel(end_label))
    
    def _generate_loop(self, loop: Loop):
        """Generate IR for a loop statement."""
        start_label = self.program.new_label()
        end_label = self.program.new_label()
        
        # Save current break/continue labels
        old_continue = self.continue_labels
        old_break = self.break_labels
        
        # Set new break/continue labels
        self.continue_labels = [start_label]
        self.break_labels = [end_label]
        
        # Start label
        self.current_function.add_instruction(IRLabel(start_label))
        
        # Generate condition
        condition_temp = self._generate_expression(loop.condition)
        
        # If condition is false, goto end
        neg_condition_temp = self.program.new_temp()
        self.current_function.add_instruction(IRUnary(neg_condition_temp, "!", condition_temp))
        self.current_function.add_instruction(IRCondJump(neg_condition_temp, end_label))
        
        # Generate body
        for stmt in loop.body:
            self._generate_statement(stmt)
        
        # At end of body, goto start
        self.current_function.add_instruction(IRJump(start_label))
        
        # End label
        self.current_function.add_instruction(IRLabel(end_label))
        
        # Restore break/continue labels
        self.continue_labels = old_continue
        self.break_labels = old_break
    
    def _generate_return(self, ret: Return):
        """Generate IR for a return statement."""
        if ret.value:
            value_temp = self._generate_expression(ret.value)
            self.current_function.add_instruction(IRReturn(value_temp))
        else:
            self.current_function.add_instruction(IRReturn())
    
    def _generate_procedure_call_statement(self, stmt: ProcedureCallStatement):
        """Generate IR for a procedure call statement."""
        self._generate_procedure_call(stmt.call, None)  # No destination for the result
    
    def _generate_procedure_call(self, call: ProcedureCall, dest: Optional[str]):
        """Generate IR for a procedure call expression."""
        # Generate IR for each argument
        arg_temps = []
        for arg in call.args:
            arg_temp = self._generate_expression(arg)
            arg_temps.append(arg_temp)
        
        # Handle procedure name
        proc_name = call.name
        if isinstance(proc_name, AttributeAccess):
            proc_name = f"{proc_name.name}.{proc_name.attribute}"
        
        # Add call instruction
        self.current_function.add_instruction(IRCall(dest, proc_name, arg_temps))
    
    def _generate_expression(self, expr: ASTNode) -> str:
        """Generate IR for an expression and return a temporary with the result."""
        if isinstance(expr, IntegerLiteral):
            temp = self.program.new_temp()
            self.current_function.add_instruction(IRConstant(temp, expr.value))
            return temp
        
        elif isinstance(expr, StringLiteral):
            temp = self.program.new_temp()
            str_label = self.program.add_string_literal(expr.value)
            self.current_function.add_instruction(IRConstant(temp, str_label))
            return temp
        
        elif isinstance(expr, Variable):
            # For simple variables, just return the name
            if isinstance(expr.name, str):
                return expr.name
            
            # For complex variables (like hardware registers), generate a temporary
            temp = self.program.new_temp()
            var_name = self._get_variable_name(expr)
            self.current_function.add_instruction(IRAssign(temp, var_name))
            return temp
        
        elif isinstance(expr, BinaryOp):
            left_temp = self._generate_expression(expr.left)
            right_temp = self._generate_expression(expr.right)
            
            dest_temp = self.program.new_temp()
            self.current_function.add_instruction(
                IRBinary(dest_temp, left_temp, expr.op, right_temp)
            )
            return dest_temp
        
        elif isinstance(expr, UnaryOp):
            operand_temp = self._generate_expression(expr.operand)
            
            dest_temp = self.program.new_temp()
            self.current_function.add_instruction(
                IRUnary(dest_temp, expr.op, operand_temp)
            )
            return dest_temp
        
        elif isinstance(expr, ListAccess):
            array_name = self._get_variable_name(expr.name)
            if len(expr.indices) != 1:
                raise ValueError("Multi-dimensional arrays not supported yet")
            
            index_temp = self._generate_expression(expr.indices[0])
            
            dest_temp = self.program.new_temp()
            self.current_function.add_instruction(
                IRArrayLoad(dest_temp, array_name, index_temp)
            )
            return dest_temp
        
        elif isinstance(expr, AttributeAccess):
            # Handle attribute access (usually hardware-related)
            full_name = self._get_attribute_name(expr)
            
            dest_temp = self.program.new_temp()
            self.current_function.add_instruction(IRAssign(dest_temp, full_name))
            return dest_temp
        
        elif isinstance(expr, ProcedureCall):
            dest_temp = self.program.new_temp()
            self._generate_procedure_call(expr, dest_temp)
            return dest_temp
        
        else:
            raise ValueError(f"Unsupported expression type: {type(expr)}")
    
    def _get_variable_name(self, var: Union[str, Variable, AttributeAccess, ListAccess]) -> str:
        """Get the name of a variable, handling complex cases."""
        if isinstance(var, str):
            return var
        elif isinstance(var, Variable):
            if isinstance(var.name, str):
                return var.name
            return self._get_variable_name(var.name)
        elif isinstance(var, AttributeAccess):
            return self._get_attribute_name(var)
        else:
            return str(var)
    
    def _get_attribute_name(self, attr: AttributeAccess) -> str:
        """Get the full name of an attribute access."""
        if isinstance(attr.name, str):
            return f"{attr.name}.{attr.attribute}"
        elif isinstance(attr.name, AttributeAccess):
            return f"{self._get_attribute_name(attr.name)}.{attr.attribute}"
        elif hasattr(attr.name, 'name'):
            return f"{attr.name.name}.{attr.attribute}"
        else:
            return f"{attr.name}.{attr.attribute}"