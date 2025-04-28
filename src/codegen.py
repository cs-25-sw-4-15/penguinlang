from RegisterAllocater import RegisterAllocator
from ast_classes import ASTNode, Program, Declaration, Assignment, Initialization, Conditional, Loop, ProcedureDef, Return, ProcedureCall, BinaryOp, UnaryOp, IntegerLiteral, StringLiteral, Variable, ListAccess
from ast_classes import VoidType, IntType, StringType, TilesetType, TileMapType, SpriteType, OAMEntryType, ListType
class GameBoyCodeGenerator(ASTNode):
    
    """Generates GameBoy Z80 assembly code from Penguin AST."""
    
    def __init__(self):
        self.register_allocator = RegisterAllocator()
        self.code = []
        self.label_counter = 0
        self.current_scope = "global"
        self.var_types = {}  # Track variable types
        
    def generate(self, ast_node):
        """Entry point for code generation."""
        self.emit_header()
        self.visit(ast_node)
        self.emit_footer()
        return '\n'.join(self.code)
    
    def emit(self, instruction):
        """Add an instruction to the output code."""
        self.code.append(instruction)
    
    def emit_header(self):
        """Emit the header section of the GameBoy ROM."""
        self.emit("; GameBoy ROM generated from Penguin language")
        self.emit("SECTION \"ROM0\", ROM0")
        self.emit("INCLUDE \"hardware.inc\"")  # Common GB hardware definitions
        
        # ROM header
        self.emit("\nSECTION \"Header\", ROM0[$100]")
        self.emit("    jp EntryPoint")
        self.emit("    ds $150 - @, 0  ; Make room for the header")
        
        # Program entry point
        self.emit("\nEntryPoint:")
        self.emit("    di  ; Disable interrupts")
        self.emit("    ld sp, $FFFE  ; Set stack pointer")
        self.emit("    call Main")
        self.emit("    jp Halt")
    
    def emit_footer(self):
        """Emit the footer section of the GameBoy ROM."""
        self.emit("\nHalt:")
        self.emit("    halt")
        self.emit("    jp Halt")
    
    def new_label(self, prefix="label"):
        """Generate a new unique label."""
        self.label_counter += 1
        return f"{prefix}_{self.label_counter}"
    
    # Visit methods for each AST node type
    
    def visit_Program(self, node):
        """Visit Program node."""
        # Create main function
        self.emit("\nMain:")
        
        # Process all statements
        for statement in node.statements:
            self.visit(statement)
        
        # Return from main
        self.emit("    ret")
    
    def visit_Declaration(self, node):
        """Visit Declaration node."""
        # Track variable type
        self.var_types[node.name] = node.type_
        
        # No actual code generation for declarations
        self.emit(f"    ; Declaration of {node.name} as {node.type_}")
    
    def visit_Assignment(self, node):
        """Visit Assignment node."""
        # Generate code for the right-hand side expression
        result_reg = self.visit_Expression(node.value)
        
        # Handle different target types
        if isinstance(node.target, Variable):
            var_name = node.target.name
            
            # Track variable type if not already tracked
            if var_name not in self.var_types:
                self.var_types[var_name] = "unknown"
            
            # Allocate location for the variable
            location = self.register_allocator.get_variable_location(var_name)
            
            if not location:
                # First time assignment, try to keep in register
                self.register_allocator.allocate_register(var_name)
                location = self.register_allocator.get_variable_location(var_name)
            
            if location['type'] == 'register':
                if location['location'] != result_reg:
                    self.emit(f"    ld {location['location']}, {result_reg}")
            else:  # memory
                self.emit(f"    ld hl, {location['location']}")
                self.emit(f"    ld [hl], {result_reg}")
                
        elif isinstance(node.target, ListAccess):
            # Handle list access
            self.emit(f"    ; List assignment not fully implemented")
            # Would need to calculate offset and store value
            
        # Free result register if different from target
        self.register_allocator.free_register(result_reg)
            
    def visit_Initialization(self, node):
        """Visit Initialization node."""
        # Track variable type
        self.var_types[node.name] = node.type_
        
        # Generate code for the initialization value
        result_reg = self.visit_Expression(node.value)
        
        # Allocate location for the variable
        self.register_allocator.allocate_register(node.name)
        location = self.register_allocator.get_variable_location(node.name)
        
        if location['type'] == 'register':
            if location['location'] != result_reg:
                self.emit(f"    ld {location['location']}, {result_reg}")
        else:  # memory
            self.emit(f"    ld hl, {location['location']}")
            self.emit(f"    ld [hl], {result_reg}")
            
        # Free result register if different from target
        if location['type'] == 'register' and location['location'] != result_reg:
            self.register_allocator.free_register(result_reg)
    
    def visit_Conditional(self, node):
        """Visit Conditional node."""
        else_label = self.new_label("else")
        end_label = self.new_label("endif")
        
        # Generate condition code
        condition_reg = self.visit_Expression(node.condition)
        
        # Test condition (compare with 0)
        self.emit(f"    ld a, {condition_reg}")
        self.emit("    or a")  # sets Z flag if A is 0
        self.emit(f"    jp z, {else_label}")
        
        # Free condition register
        self.register_allocator.free_register(condition_reg)
        
        # Generate "then" block
        for stmt in node.then_statements:
            self.visit(stmt)
            
        self.emit(f"    jp {end_label}")
        
        # Generate "else" block if it exists
        self.emit(f"{else_label}:")
        if node.else_statements:
            for stmt in node.else_statements:
                self.visit(stmt)
                
        self.emit(f"{end_label}:")
    
    def visit_Loop(self, node):
        """Visit Loop node."""
        loop_start = self.new_label("loop_start")
        loop_end = self.new_label("loop_end")
        
        self.emit(f"{loop_start}:")
        
        # Generate condition code
        condition_reg = self.visit_Expression(node.condition)
        
        # Test condition (compare with 0)
        self.emit(f"    ld a, {condition_reg}")
        self.emit("    or a")  # sets Z flag if A is 0
        self.emit(f"    jp z, {loop_end}")
        
        # Free condition register
        self.register_allocator.free_register(condition_reg)
        
        # Generate loop body
        for stmt in node.statements:
            self.visit(stmt)
            
        self.emit(f"    jp {loop_start}")
        self.emit(f"{loop_end}:")
    
    def visit_ProcedureDef(self, node):
        """Visit ProcedureDef node."""
        prev_scope = self.current_scope
        self.current_scope = node.name
        
        self.emit(f"\n{node.name}:")
        
        # Save registers that will be used
        self.emit("    push bc")
        self.emit("    push de")
        self.emit("    push hl")
        
        # Process parameters
        for i, (param_type, param_name) in enumerate(node.parameters):
            self.var_types[param_name] = param_type
            
            # Parameters are passed on stack in GB assembly
            # Would need more complex stack frame handling in real implementation
            
        # Process procedure statements
        for stmt in node.statements:
            self.visit(stmt)
        
        # Restore registers
        self.emit("    pop hl")
        self.emit("    pop de")
        self.emit("    pop bc")
        self.emit("    ret")
        
        self.current_scope = prev_scope
    
    def visit_Return(self, node):
        """Visit Return node."""
        result_reg = self.visit_Expression(node.value)
        
        # Move result to accumulator (a typical convention for return values)
        if result_reg != 'a':
            self.emit(f"    ld a, {result_reg}")
        
        # Free result register
        self.register_allocator.free_register(result_reg)
        
        # Return from procedure
        self.emit("    pop hl")
        self.emit("    pop de")
        self.emit("    pop bc")
        self.emit("    ret")
    
    def visit_ProcedureCall(self, node):
        """Visit ProcedureCall node."""
        # Evaluate and push arguments (in reverse order for stack)
        for arg in reversed(node.args):
            arg_reg = self.visit_Expression(arg)
            self.emit(f"    push {arg_reg}")
            self.register_allocator.free_register(arg_reg)
        
        # Call the procedure
        if isinstance(node.name, Variable):
            self.emit(f"    call {node.name.name}")
        else:
            # More complex name resolution needed
            self.emit(f"    ; Complex procedure call not fully implemented")
        
        # Clean up stack if needed
        if node.args:
            self.emit(f"    add sp, {len(node.args) * 2}")  # 2 bytes per argument
        
        # Result is in register A by convention
        return 'a'
    
    def visit_BinaryOp(self, node):
        """Visit BinaryOp node."""
        # Evaluate left operand
        left_reg = self.visit_Expression(node.left)
        
        # Special case optimization for common operations
        if node.op in ['+', '-', '&', '|', '^'] and isinstance(node.right, IntegerLiteral):
            if node.op == '+':
                self.emit(f"    ld a, {left_reg}")
                self.emit(f"    add {node.right.value}")
            elif node.op == '-':
                self.emit(f"    ld a, {left_reg}")
                self.emit(f"    sub {node.right.value}")
            # Other operations similarly
            
            self.register_allocator.free_register(left_reg)
            return 'a'
        
        # General case: evaluate right operand
        right_reg = self.visit_Expression(node.right)
        
        # Generate operation code
        if node.op == '+':
            self.emit(f"    ld a, {left_reg}")
            self.emit(f"    add {right_reg}")
        elif node.op == '-':
            self.emit(f"    ld a, {left_reg}")
            self.emit(f"    sub {right_reg}")
        elif node.op == '*':
            # GB CPU has no multiply instruction, would need a subroutine
            self.emit(f"    ld b, {left_reg}")
            self.emit(f"    ld c, {right_reg}")
            self.emit(f"    call Multiply")  # Would need to implement this routine
        # Handle comparison, logical, and other operators...
        
        # Free operand registers
        self.register_allocator.free_register(left_reg)
        self.register_allocator.free_register(right_reg)
        
        # Result is in register A
        return 'a'
    
    def visit_UnaryOp(self, node):
        """Visit UnaryOp node."""
        # Evaluate operand
        operand_reg = self.visit_Expression(node.right)
        
        # Generate operation code
        if node.op == '-':
            self.emit(f"    ld a, {operand_reg}")
            self.emit("    cpl")  # One's complement
            self.emit("    inc a")  # Two's complement for negation
        elif node.op == '!':
            self.emit(f"    ld a, {operand_reg}")
            self.emit("    or a")  # Set flags based on A
            self.emit("    ld a, 0")  # Assume result is false
            self.emit("    jp nz, $+4")  # Skip next instruction if not zero
            self.emit("    inc a")  # Set A to 1 if operand was zero
        # Other unary operators...
        
        # Free operand register
        self.register_allocator.free_register(operand_reg)
        
        # Result is in register A
        return 'a'
    
    def visit_IntegerLiteral(self, node):
        """Visit IntegerLiteral node."""
        # Put literal in register A (common practice)
        self.emit(f"    ld a, {node.value}")
        return 'a'
    
    def visit_StringLiteral(self, node):
        """Visit StringLiteral node."""
        # Create a label for the string in data section
        string_label = self.new_label("string")
        
        # Store string definition for later emission in data section
        # (This is simplified - would need proper string data handling)
        self.emit(f"; String literal: {node.value}")
        
        # Load string address into HL
        self.emit(f"    ld hl, {string_label}")
        return 'hl'  # HL now contains string address
    
    def visit_Variable(self, node):
        """Visit Variable node."""
        var_name = node.name
        location = self.register_allocator.get_variable_location(var_name)
        
        if not location:
            # First reference to variable, try to allocate register
            self.register_allocator.allocate_register(var_name)
            location = self.register_allocator.get_variable_location(var_name)
            
            if not location:
                # Could not allocate - error or default handling
                self.emit(f"    ; ERROR: Cannot locate variable {var_name}")
                return 'a'
        
        if location['type'] == 'register':
            return location['location']
        else:  # memory
            self.emit(f"    ld hl, {location['location']}")
            self.emit("    ld a, [hl]")
            return 'a'
    
    def visit_ListAccess(self, node):
        """Visit ListAccess node."""
        # Calculate base address
        if isinstance(node.name, Variable):
            base_var = node.name.name
            self.emit(f"    ; Accessing list {base_var}")
            
            # Load base address
            location = self.register_allocator.get_variable_location(base_var)
            if location and location['type'] == 'memory':
                self.emit(f"    ld hl, {location['location']}")
            else:
                self.emit(f"    ; ERROR: Cannot locate list {base_var}")
                return 'a'
        else:
            # More complex base address calculation
            self.emit(f"    ; Complex list access not fully implemented")
            return 'a'
        
        # Calculate offset for each index
        for idx in node.indices:
            # Evaluate index expression
            idx_reg = self.visit_Expression(idx)
            
            # Add offset to base address (would need multiply by element size)
            self.emit(f"    ld b, 0")
            self.emit(f"    ld c, {idx_reg}")
            self.emit("    add hl, bc")
            
            self.register_allocator.free_register(idx_reg)
        
        # Load value from calculated address
        self.emit("    ld a, [hl]")
        return 'a'
    
    def visit_Expression(self, node):
        """Visit Expression node by dispatching to appropriate handler."""
        if isinstance(node, BinaryOp):
            return self.visit_BinaryOp(node)
        elif isinstance(node, UnaryOp):
            return self.visit_UnaryOp(node)
        elif isinstance(node, IntegerLiteral):
            return self.visit_IntegerLiteral(node)
        elif isinstance(node, StringLiteral):
            return self.visit_StringLiteral(node)
        elif isinstance(node, Variable):
            return self.visit_Variable(node)
        elif isinstance(node, ListAccess):
            return self.visit_ListAccess(node)
        elif isinstance(node, ProcedureCall):
            return self.visit_ProcedureCall(node)
        else:
            self.emit(f"    ; ERROR: Unknown expression type {type(node)}")
            return 'a'
    
    # Add visit methods for other AST node types as needed