from RegisterAllocater import RegisterAllocator
from ast_classes import ASTNode, ProcedureCall, BinaryOp, UnaryOp, IntegerLiteral, StringLiteral, Variable, ListAccess, AttributeAccess
from asttypes import SpriteType, TileMapType, TilesetType

class CodeGenerator:
    """Generates GameBoy Z80 assembly code from Penguin AST."""
    
    def __init__(self):
        self.register_allocator = RegisterAllocator()
        self.code = []
        self.label_counter = 0
        self.current_scope = "global"
        self.var_types = {}  # Track variable types
        self.binary_imports = {}  # Track binary imports with more info: {path: {label, size_var, type}}
        self.binary_var_mapping = {}  # Map variable names to binary import paths
        self.vram_allocation = {
            'tileset': 0,  # Track how much VRAM is used by tilesets
            'tilemap': 0,  # Track how much VRAM is used by tilemaps
            'sprites': 0   # Track how much VRAM is used by sprites
        }
        self.predefined_macros = {
            "control.waitforvblank": self._macro_wait_for_vblank,
            "control.lcdon": self._macro_lcd_on,
            "control.lcdoff": self._macro_lcd_off
        }
        
    def generate(self, ast_node):
        """Entry point for code generation."""
        self.emit_header()
        self.visit(ast_node)
        self.emit_binary_imports()  # Add binary imports section
        self.emit_vram_helpers()    # Add VRAM copy helpers
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
    
    def emit_binary_imports(self):
        """Emit binary imports section."""
        if not self.binary_imports:
            return
            
        self.emit("\n; Binary data imports")
        for binary_file, info in self.binary_imports.items():
            # Use the stored label for this binary file
            file_label = info['label']
            self.emit(f"\n{file_label}:")
            self.emit(f"    INCBIN \"{binary_file}\"")
            self.emit(f"{file_label}_end:")
            
            # Generate a size constant for this binary file
            size_label = info['size_var']
            self.emit(f"{size_label} EQU {file_label}_end - {file_label}")
    
    def emit_vram_helpers(self):
        """Emit helper functions for VRAM operations."""
        # Common routine for copying data to VRAM
        self.emit("\n; VRAM copy helper routine")
        self.emit("CopyToVRAM:")
        self.emit("    ; Inputs: HL = source, DE = destination, BC = size")
        
        # Wait for VBLANK before VRAM access
        wait_label = self.new_label("wait_vblank_helper")
        self.emit(f"{wait_label}:")
        self.emit("    ldh a, [rLY]")
        self.emit("    cp 144")
        self.emit(f"    jr c, {wait_label}")
        
        # Turn LCD off
        self.emit("    ldh a, [rLCDC]")
        self.emit("    push af  ; Save LCD state")
        self.emit("    res 7, a  ; Clear LCD on bit")
        self.emit("    ldh [rLCDC], a")
        
        # Copy loop
        copy_label = self.new_label("copy_loop")
        self.emit(f"{copy_label}:")
        self.emit("    ld a, [hl+]  ; Load byte from ROM and increment")
        self.emit("    ld [de], a   ; Store byte to VRAM")
        self.emit("    inc de       ; Next destination byte")
        self.emit("    dec bc       ; Decrement counter")
        self.emit("    ld a, b")
        self.emit("    or c")
        self.emit(f"    jr nz, {copy_label}  ; Loop until done")
        
        # Restore LCD
        self.emit("    pop af  ; Restore LCD state")
        self.emit("    ldh [rLCDC], a")
        self.emit("    ret")
    
    def _get_label_from_path(self, path):
        """Convert a file path to a valid assembly label."""
        # Remove path and extension, replace invalid characters
        base_name = path.split('/')[-1].split('\\')[-1].split('.')[0]
        valid_name = ''.join(c if c.isalnum() else '_' for c in base_name)
        return f"data_{valid_name}"
    
    def _register_binary_import(self, binary_path, asset_type):
        """Register a binary import and generate related labels."""
        if binary_path not in self.binary_imports:
            file_label = self._get_label_from_path(binary_path)
            size_label = f"{file_label}_size"
            
            self.binary_imports[binary_path] = {
                'label': file_label,
                'size_var': size_label,
                'type': asset_type
            }
            
        return self.binary_imports[binary_path]
    
    def new_label(self, prefix="label"):
        """Generate a new unique label."""
        self.label_counter += 1
        return f"{prefix}_{self.label_counter}"
    
    def _macro_wait_for_vblank(self):
        """Macro for waiting for VBLANK interrupt."""
        wait_label = self.new_label("wait_vblank")
        self.emit(f"{wait_label}:")
        self.emit("    ldh a, [rLY]  ; Load current scanline")
        self.emit("    cp 144        ; Check if in VBlank (scanline >= 144)")
        self.emit(f"    jr c, {wait_label}  ; Loop if not in VBlank")
        return None  # No result register needed
    
    def _macro_lcd_on(self):
        """Macro for turning LCD on."""
        self.emit("    ldh a, [rLCDC]")
        self.emit("    set 7, a      ; Set LCD on bit (bit 7)")
        self.emit("    ldh [rLCDC], a")
        return None  # No result register needed
    
    def _macro_lcd_off(self):
        """Macro for turning LCD off."""
        wait_label = self.new_label("wait_vblank_off")
        self.emit(f"; Wait for VBlank before turning LCD off")
        self.emit(f"{wait_label}:")
        self.emit("    ldh a, [rLY]")
        self.emit("    cp 144")
        self.emit(f"    jr c, {wait_label}")
        self.emit("    ldh a, [rLCDC]")
        self.emit("    res 7, a      ; Clear LCD on bit (bit 7)")
        self.emit("    ldh [rLCDC], a")
        return None  # No result register needed
    
    def _generate_copy_to_vram_code(self, source_label, dest_address, size_var=None):
        """Generate code to copy data from ROM to VRAM."""
        # Use the common helper routine
        self.emit(f"    ; Copying data to VRAM at {dest_address}")
        self.emit(f"    ld hl, {source_label}  ; Source address")
        self.emit(f"    ld de, {dest_address}  ; Destination address in VRAM")
        
        # Set up size
        if size_var:
            self.emit(f"    ld bc, {size_var}  ; Size")
        else:
            self.emit(f"    ld bc, {source_label}_end - {source_label}  ; Size")
        
        # Call helper
        self.emit("    call CopyToVRAM")
        
    def _resolve_qualified_name(self, node):
        """Resolve the full qualified name for a variable, attribute access, or list access node."""
        if isinstance(node, Variable):
            return node.name
        elif isinstance(node, AttributeAccess):
            # Get base name and combine with attribute
            base_name = self._resolve_qualified_name(node.name) if not isinstance(node.name, str) else node.name
            return f"{base_name}.{node.attribute}"
        elif isinstance(node, ListAccess):
            # Get base name for list
            base_name = self._resolve_qualified_name(node.name) if not isinstance(node.name, str) else node.name
            return base_name
        elif isinstance(node, str):
            return node
        else:
            self.emit(f"    ; WARNING: Unknown node type for name resolution: {type(node)}")
            return "unknown"
    
    def _extract_indices(self, node):
        """Extract indices from a ListAccess node."""
        if isinstance(node, ListAccess):
            return node.indices
        return []
    
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
        self.var_types[node.name] = node.var_type
        
        # No actual code generation for declarations
        self.emit(f"    ; Declaration of {node.name} as {node.var_type}")
    
    def visit_Assignment(self, node):
        """Visit Assignment node."""
        # Get the full qualified name for the target
        qualified_name = self._resolve_qualified_name(node.target)
        
        # Handle special case for display.tileset0, display.tilemap0, etc.
        if qualified_name.startswith("display."):
            target_type = None
            dest_address = None
            
            if qualified_name == "display.tileset0":
                target_type = "tileset"
                dest_address = "$8000"  # Tile data in VRAM
                self.emit(f"    ; Loading tileset to VRAM at 8000")
            elif qualified_name == "display.tilemap0":
                target_type = "tilemap"
                dest_address = "$9800"  # Background tilemap in VRAM
                self.emit(f"    ; Loading tilemap to VRAM at 9800")
            elif qualified_name == "display.sprites":
                target_type = "sprites"
                # Sprite data in VRAM - after any tilesets
                if self.vram_allocation['tileset'] > 0:
                    offset = self.vram_allocation['tileset']
                    dest_address = f"$8000 + {offset}"
                    self.emit(f"    ; Loading sprites to VRAM at 8000 + {offset} bytes")
                else:
                    dest_address = "$8000"
                    self.emit(f"    ; Loading sprites to VRAM at 8000")
            
            if target_type:
                # Check if the value is a variable that references a binary file
                var_name = None
                binary_path = None
                
                if isinstance(node.value, Variable):
                    var_name = node.value.name
                    # Check if we know the binary path for this variable
                    if var_name in self.binary_var_mapping:
                        binary_path = self.binary_var_mapping[var_name]
                
                if binary_path:
                    # Use the registered binary import
                    import_info = self.binary_imports[binary_path]
                    file_label = import_info['label']
                    size_var = import_info['size_var']
                    
                    # Generate code to copy from ROM to VRAM
                    self._generate_copy_to_vram_code(file_label, dest_address, size_var)
                    
                    # Update VRAM allocation
                    if target_type == "tileset":
                        self.vram_allocation['tileset'] += 3072  # Typical tileset size (3KB)
                    elif target_type == "tilemap":
                        self.vram_allocation['tilemap'] += 1024  # 32x32 tilemap size
                    elif target_type == "sprites":
                        self.vram_allocation['sprites'] += 1024  # Approx sprite data size
                    
                    return
        
        # Regular assignment handling for other cases
        result_reg = self.visit_Expression(node.value)
        
        # Handle different target types based on its structure
        if isinstance(node.target, Variable):
            # Track variable type if not already tracked
            if qualified_name not in self.var_types:
                self.var_types[qualified_name] = node.target.var_type
            
            # Allocate location for the variable
            location = self.register_allocator.get_variable_location(qualified_name)
            
            if not location:
                # First time assignment, try to keep in register
                self.register_allocator.allocate_register(qualified_name)
                location = self.register_allocator.get_variable_location(qualified_name)
            
            if location['type'] == 'register':
                if location['location'] != result_reg:
                    self.emit(f"    ld {location['location']}, {result_reg}")
            else:  # memory
                self.emit(f"    ld hl, {location['location']}")
                self.emit(f"    ld [hl], {result_reg}")
                
        elif isinstance(node.target, ListAccess) or isinstance(node.target, AttributeAccess):
            indices = self._extract_indices(node.target)
            
            self.emit(f"    ; Assignment to {qualified_name}")
            
            # Load base address
            location = self.register_allocator.get_variable_location(qualified_name)
            if location and location['type'] == 'memory':
                self.emit(f"    ld hl, {location['location']}")
            else:
                self.emit(f"    ld hl, {qualified_name}")  # Assuming it's a global variable
            
            # Calculate offset for each index if this is a list access
            for idx in indices:
                # Evaluate index expression
                idx_reg = self.visit_Expression(idx)
                
                # Add offset to base address (would need multiply by element size)
                self.emit(f"    ld b, 0")
                self.emit(f"    ld c, {idx_reg}")
                self.emit("    add hl, bc")
                
                self.register_allocator.free_register(idx_reg)
            
            # Store the value at the calculated address
            self.emit(f"    ld [hl], {result_reg}")
                
        # Free result register
        if result_reg:  # Only free if a register was allocated
            self.register_allocator.free_register(result_reg)
            
    def visit_Initialization(self, node):
        """Visit Initialization node."""
        # Track variable type
        self.var_types[node.name] = node.var_type
        
        # Special handling for binary assets (tileset, tilemap, sprites)
        if isinstance(node.var_type, (TilesetType, TileMapType, SpriteType)):
            if isinstance(node.value, StringLiteral):
                # Get the binary file path
                binary_path = node.value.value
                
                # Register the binary import with appropriate type
                asset_type = None
                if isinstance(node.var_type, TilesetType):
                    asset_type = "tileset"
                elif isinstance(node.var_type, TileMapType):
                    asset_type = "tilemap"
                elif isinstance(node.var_type, SpriteType):
                    asset_type = "sprites"
                
                import_info = self._register_binary_import(binary_path, asset_type)
                
                # Map this variable to the binary path for later reference
                self.binary_var_mapping[node.name] = binary_path
                
                self.emit(f"    ; Binary asset {node.name} initialized from {binary_path}")
                
                # Allocate memory location for this variable
                self.register_allocator.spill_variable(node.name)
                return
        
        # Regular initialization for other cases
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
        if result_reg and location['type'] == 'register' and location['location'] != result_reg:
            self.register_allocator.free_register(result_reg)
    
    def visit_ListInitialization(self, node):
        """Visit ListInitialization node."""
        # Allocate memory for the list (implementation depends on runtime)
        list_size = len(node.values)
        self.emit(f"    ; Initializing list {node.name} with {list_size} elements")
        
        # For simplicity, we'll just generate a global label for the list
        self.emit(f"{node.name}:")
        
        # Emit each value in the list
        for value in node.values:
            if isinstance(value, IntegerLiteral):
                self.emit(f"    db {value.value}  ; Integer literal")
            #IF LIST ITEM IS EXPRESSION OF LITERALS, HANDLE HERE
            #elif isinstance(value, Expression):
                #self.emit(f"    db \"{value.value}\", 0  ; String literal with null terminator")
            else:
                self.emit(f"    db 0  ; Variables currently not supported in lists")
    
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
        if condition_reg:
            self.register_allocator.free_register(condition_reg)
        
        # Generate "then" block
        for stmt in node.then_body:
            self.visit(stmt)
            
        self.emit(f"    jp {end_label}")
        
        # Generate "else" block if it exists
        self.emit(f"{else_label}:")
        if node.else_body:
            for stmt in node.else_body:
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
        if condition_reg:
            self.register_allocator.free_register(condition_reg)
        
        # Generate loop body
        for stmt in node.body:
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
        
        # Process parameters - in AST, params are stored as tuples (type, name)
        for param_type, param_name in node.params:
            self.var_types[param_name] = param_type
            
            # Parameters are passed on stack in GB assembly
            # Would need more complex stack frame handling in real implementation
            
        # Process procedure body
        for stmt in node.body:
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
        if result_reg and result_reg != 'a':
            self.emit(f"    ld a, {result_reg}")
        
        # Free result register
        if result_reg:
            self.register_allocator.free_register(result_reg)
        
        # Return from procedure
        self.emit("    pop hl")
        self.emit("    pop de")
        self.emit("    pop bc")
        self.emit("    ret")
    
    def visit_ProcedureCall(self, node):
        """Visit ProcedureCall node."""
        # Get the full qualified name for the procedure
        procedure_name = self._resolve_qualified_name(node.name)
            
        # Handle predefined macros
        if procedure_name in self.predefined_macros:
            self.emit(f"    ; Predefined function: {procedure_name}")
            return self.predefined_macros[procedure_name]()
            
        # Evaluate and push arguments (in reverse order for stack)
        for arg in reversed(node.args):
            arg_reg = self.visit_Expression(arg)
            if arg_reg:
                self.emit(f"    push {arg_reg}")
                self.register_allocator.free_register(arg_reg)
        
        # Call the procedure
        self.emit(f"    call {procedure_name}")
        
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
            elif node.op == '&':
                self.emit(f"    ld a, {left_reg}")
                self.emit(f"    and {node.right.value}")
            elif node.op == '|':
                self.emit(f"    ld a, {left_reg}")
                self.emit(f"    or {node.right.value}")
            elif node.op == '^':
                self.emit(f"    ld a, {left_reg}")
                self.emit(f"    xor {node.right.value}")
            
            if left_reg:
                self.register_allocator.free_register(left_reg)
            return 'a'
    
    def visit_ListAccess(self, node):
        """Visit ListAccess node."""
        # Get the base qualified name
        base_var = self._resolve_qualified_name(node)
        
        self.emit(f"    ; Accessing list {base_var}")
        
        # Load base address
        location = self.register_allocator.get_variable_location(base_var)
        if location and location['type'] == 'memory':
            self.emit(f"    ld hl, {location['location']}")
        else:
            self.emit(f"    ld hl, {base_var}")  # Assuming it's a global variable
        
        # Calculate offset for each index
        indices = self._extract_indices(node)
        for idx in indices:
            # Evaluate index expression
            idx_reg = self.visit_Expression(idx)
            
            # Add offset to base address (would need multiply by element size)
            self.emit(f"    ld b, 0")
            self.emit(f"    ld c, {idx_reg}")
            self.emit("    add hl, bc")
            
            if idx_reg:
                self.register_allocator.free_register(idx_reg)
        
        # Load value from calculated address
        self.emit("    ld a, [hl]")
        return 'a'
    
    def visit_AttributeAccess(self, node):
        """Visit AttributeAccess node."""
        # Get the full qualified name
        qualified_name = self._resolve_qualified_name(node)
        
        self.emit(f"    ; Accessing attribute {qualified_name}")
        
        # For hardware-specific attributes like OAM entries (sprites)
        parts = qualified_name.split('.')
        if len(parts) > 1:
            obj_name = parts[0]
            attr_name = parts[-1]
            
            # For OAM entries like sprite.x, sprite.y, sprite.tile
            # We'd need to calculate the proper offset based on the attribute
            offset = 0
            if attr_name == 'x':
                offset = 0
            elif attr_name == 'y':
                offset = 1
            elif attr_name == 'tile':
                offset = 2
            else:
                self.emit(f"    ; Unknown attribute {attr_name}")
            
            # Load base address
            location = self.register_allocator.get_variable_location(obj_name)
            if location and location['type'] == 'memory':
                self.emit(f"    ld hl, {location['location']}")
            else:
                self.emit(f"    ld hl, {obj_name}")  # Assuming it's a global variable
                
            # Add attribute offset
            if offset > 0:
                self.emit(f"    ld bc, {offset}")
                self.emit("    add hl, bc")
                
            # Load the attribute value
            self.emit("    ld a, [hl]")
            return 'a'
        else:
            # Just a simple variable reference
            return self.visit_Variable(Variable(qualified_name))
    
    def visit_ProcedureCallStatement(self, node):
        """Visit ProcedureCallStatement node."""
        # Get the procedure call's full qualified name
        procedure_name = self._resolve_qualified_name(node.call.name) if not isinstance(node.call.name, str) else node.call.name
            
        # Handle predefined macros
        if procedure_name in self.predefined_macros:
            self.emit(f"    ; Predefined function: {procedure_name}")
            result_reg = self.predefined_macros[procedure_name]()
            if result_reg:
                self.register_allocator.free_register(result_reg)
            return
            
        # Call the ProcedureCall visitor on the call attribute
        result_reg = self.visit_ProcedureCall(node.call)
        
        # Free the result register since we're not saving the return value
        if result_reg:
            self.register_allocator.free_register(result_reg)
    
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
        elif isinstance(node, AttributeAccess):
            return self.visit_AttributeAccess(node) 
        else:
            self.emit(f"    ; ERROR: Unknown expression type {type(node)}")
            return 'a'
    
    def visit(self, node):
        """Generic visitor that dispatches to specific visitor methods."""
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, None)
    
        if visitor is None:
            raise ValueError(f"No visitor method found for {type(node).__name__}")
    
        return visitor(node)
        
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
        elif node.op == '/':
            # GB CPU has no divide instruction, would need a subroutine
            self.emit(f"    ld b, {left_reg}")
            self.emit(f"    ld c, {right_reg}")
            self.emit(f"    call Divide")  # Would need to implement this routine
        elif node.op == '&':
            self.emit(f"    ld a, {left_reg}")
            self.emit(f"    and {right_reg}")
        elif node.op == '|':
            self.emit(f"    ld a, {left_reg}")
            self.emit(f"    or {right_reg}")
        elif node.op == '^':
            self.emit(f"    ld a, {left_reg}")
            self.emit(f"    xor {right_reg}")
        elif node.op in ['==', '!=', '<', '>', '<=', '>=']:
            self.emit(f"    ld a, {left_reg}")
            self.emit(f"    cp {right_reg}")
            
            # Set A to 1 (true) or 0 (false) based on the comparison
            if node.op == '==':
                self.emit("    ld a, 0")  # Assume result is false
                self.emit("    jp nz, $+4")  # Skip next instruction if not equal
                self.emit("    inc a")  # Set A to 1 if equal
            elif node.op == '!=':
                self.emit("    ld a, 0")  # Assume result is false
                self.emit("    jp z, $+4")  # Skip next instruction if equal
                self.emit("    inc a")  # Set A to 1 if not equal
            elif node.op == '<':
                self.emit("    ld a, 0")  # Assume result is false
                self.emit("    jp nc, $+4")  # Skip next instruction if not carry (>=)
                self.emit("    inc a")  # Set A to 1 if carry (< condition)
            elif node.op == '>=':
                self.emit("    ld a, 0")  # Assume result is false
                self.emit("    jp c, $+4")  # Skip next instruction if carry (<)
                self.emit("    inc a")  # Set A to 1 if not carry (>= condition)
            elif node.op == '>':
                self.emit("    ld a, 0")  # Assume result is false
                self.emit("    jp z, $+7")  # Skip to the end if equal
                self.emit("    jp c, $+4")  # Skip next instruction if carry (<)
                self.emit("    inc a")  # Set A to 1 if not carry and not zero (> condition)
            elif node.op == '<=':
                self.emit("    ld a, 1")  # Assume result is true
                self.emit("    jp z, $+7")  # Skip to the end if equal (already true)
                self.emit("    jp nc, $+4")  # Skip next instruction if not carry (>)
                self.emit("    dec a")  # Set A to 0 if not carry and not zero (> condition)
        
        # Free operand registers
        if left_reg:
            self.register_allocator.free_register(left_reg)
        if right_reg:
            self.register_allocator.free_register(right_reg)
        
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
        self.emit(f"\n{string_label}:")
        self.emit(f"    db \"{node.value}\", 0  ; String with null terminator")
        
        # Load string address into HL
        self.emit(f"    ld hl, {string_label}")
        return 'hl'  # HL now contains string address
    
    def visit_Variable(self, node):
        """Visit Variable node."""
        # Get the full qualified name
        var_name = self._resolve_qualified_name(node)
        
        self.emit(f"    ; Accessing variable {var_name}")
        
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
    
    def visit_UnaryOp(self, node):
        """Visit UnaryOp node."""
        # Evaluate operand
        operand_reg = self.visit_Expression(node.operand)
        
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
        elif node.op == '~':
            self.emit(f"    ld a, {operand_reg}")
            self.emit("    cpl")  # Bitwise NOT (one's complement)
        
        # Free operand register
        if operand_reg:
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
        self.emit(f"\n{string_label}:")
        self.emit(f"    db \"{node.value}\", 0  ; String with null terminator")
        
        # Load string address into HL
        self.emit(f"    ld hl, {string_label}")
        return 'hl'  # HL now contains string address
    
    def visit_Variable(self, node):
        """Visit Variable node."""
        # Get the full qualified name
        var_name = self._resolve_qualified_name(node)
        
        self.emit(f"    ; Accessing variable {var_name}")
        
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
        # Get the base qualified name
        base_var = self._resolve_qualified_name(node)
        
        self.emit(f"    ; Accessing list {base_var}")
        
        # Load base address
        location = self.register_allocator.get_variable_location(base_var)
        if location and location['type'] == 'memory':
            self.emit(f"    ld hl, {location['location']}")
        else:
            self.emit(f"    ld hl, {base_var}")  # Assuming it's a global variable
        
        # Calculate offset for each index
        indices = self._extract_indices(node)
        for idx in indices:
            # Evaluate index expression
            idx_reg = self.visit_Expression(idx)
            
            # Add offset to base address (would need multiply by element size)
            self.emit(f"    ld b, 0")
            self.emit(f"    ld c, {idx_reg}")
            self.emit("    add hl, bc")
            
            if idx_reg:
                self.register_allocator.free_register(idx_reg)
        
        # Load value from calculated address
        self.emit("    ld a, [hl]")
        return 'a'
    
    def visit_AttributeAccess(self, node):
        """Visit AttributeAccess node."""
        # Get the full qualified name
        qualified_name = self._resolve_qualified_name(node)
        
        self.emit(f"    ; Accessing attribute {qualified_name}")
        
        # For hardware-specific attributes like OAM entries (sprites)
        parts = qualified_name.split('.')
        if len(parts) > 1:
            obj_name = parts[0]
            attr_name = parts[-1]
            
            # For OAM entries like sprite.x, sprite.y, sprite.tile
            # We'd need to calculate the proper offset based on the attribute
            offset = 0
            if attr_name == 'x':
                offset = 0
            elif attr_name == 'y':
                offset = 1
            elif attr_name == 'tile':
                offset = 2
            else:
                self.emit(f"    ; Unknown attribute {attr_name}")
            
            # Load base address
            location = self.register_allocator.get_variable_location(obj_name)
            if location and location['type'] == 'memory':
                self.emit(f"    ld hl, {location['location']}")
            else:
                self.emit(f"    ld hl, {obj_name}")  # Assuming it's a global variable
                
            # Add attribute offset
            if offset > 0:
                self.emit(f"    ld bc, {offset}")
                self.emit("    add hl, bc")
                
            # Load the attribute value
            self.emit("    ld a, [hl]")
            return 'a'
        else:
            # Just a simple variable reference
            return self.visit_Variable(Variable(qualified_name))
    
    def visit_ProcedureCallStatement(self, node):
        """Visit ProcedureCallStatement node."""
        # Get the procedure call's full qualified name
        procedure_name = self._resolve_qualified_name(node.call.name) if not isinstance(node.call.name, str) else node.call.name
            
        # Handle predefined macros
        if procedure_name in self.predefined_macros:
            self.emit(f"    ; Predefined function: {procedure_name}")
            result_reg = self.predefined_macros[procedure_name]()
            if result_reg:
                self.register_allocator.free_register(result_reg)
            return
            
        # Call the ProcedureCall visitor on the call attribute
        result_reg = self.visit_ProcedureCall(node.call)
        
        # Free the result register since we're not saving the return value
        if result_reg:
            self.register_allocator.free_register(result_reg)
    
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
        elif isinstance(node, AttributeAccess):
            return self.visit_AttributeAccess(node) 
        else:
            self.emit(f"    ; ERROR: Unknown expression type {type(node)}")
            return 'a'
    
    def visit(self, node):
        """Generic visitor that dispatches to specific visitor methods."""
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, None)
    
        if visitor is None:
            raise ValueError(f"No visitor method found for {type(node).__name__}")
    
        return visitor(node)