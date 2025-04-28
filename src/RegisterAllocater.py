class RegisterAllocator:
    """Manages register allocation for GameBoy Z80-like CPU."""
    
    def __init__(self):
        # Track register availability
        self.available_registers = {
            'a': True,  # Accumulator
            'b': True, 'c': True,  # General purpose
            'd': True, 'e': True,  # General purpose
            'h': True, 'l': True,  # Often used for memory addressing
            # Register pairs are implicit
        }
        
        # Special registers not typically allocated directly
        self.special_registers = ['sp', 'pc']
        
        # Track register-variable mapping
        self.register_map = {}
        self.variable_map = {}
        
        # Track variables that need to be spilled to memory
        self.spilled_vars = set()
        self.memory_map = {}  # Variable to memory address mapping
        self.next_memory_addr = 0xC000  # Starting RAM address
        
    def allocate_register(self, var_name, preferred=None):
        """Allocate a register for a variable."""
        # Check if variable is already allocated
        if var_name in self.variable_map:
            return self.variable_map[var_name]
        
        # Try preferred register first if specified
        if preferred and self.available_registers.get(preferred, False):
            self.available_registers[preferred] = False
            self.register_map[preferred] = var_name
            self.variable_map[var_name] = preferred
            return preferred
            
        # Try to allocate any available register
        for reg in ['h', 'l', 'd', 'e', 'b', 'c', 'a']:  # Order by preference
            if self.available_registers[reg]:
                self.available_registers[reg] = False
                self.register_map[reg] = var_name
                self.variable_map[var_name] = reg
                return reg
        
        # No registers available, spill to memory
        self.spill_variable(var_name)
        return None
    
    def free_register(self, register=None, var_name=None):
        """Free a register by register name or variable name."""
        if register and register in self.register_map:
            var = self.register_map[register]
            del self.register_map[register]
            if var in self.variable_map:
                del self.variable_map[var]
            self.available_registers[register] = True
            return True
            
        if var_name and var_name in self.variable_map:
            reg = self.variable_map[var_name]
            del self.variable_map[var_name]
            del self.register_map[reg]
            self.available_registers[reg] = True
            return True
            
        return False
    
    def spill_variable(self, var_name):
        """Spill a variable to memory."""
        self.spilled_vars.add(var_name)
        self.memory_map[var_name] = self.next_memory_addr
        self.next_memory_addr += 2  # Allocate 2 bytes (typical for int)
    
    def get_variable_location(self, var_name):
        """Get location (register or memory address) of a variable."""
        if var_name in self.variable_map:
            return {'type': 'register', 'location': self.variable_map[var_name]}
        elif var_name in self.memory_map:
            return {'type': 'memory', 'location': self.memory_map[var_name]}
        return None
    
    def ensure_register(self, var_name, target_reg=None):
        """Ensure a variable is in a register, loading from memory if needed."""
        # If variable is already in a register
        if var_name in self.variable_map:
            current_reg = self.variable_map[var_name]
            
            # If targeting a specific register and it's different
            if target_reg and current_reg != target_reg:
                # Need to move between registers
                return {
                    'type': 'move_registers',
                    'from': current_reg,
                    'to': target_reg
                }
            
            return {'type': 'already_in_register', 'register': current_reg}
        
        # Variable is in memory, need to load
        if var_name in self.memory_map:
            # Decide which register to load into
            dest_reg = target_reg if target_reg else self.allocate_register(var_name)
            
            if not dest_reg:
                # No register available even after trying to allocate
                return {'type': 'no_register_available'}
                
            return {
                'type': 'load_from_memory',
                'memory_addr': self.memory_map[var_name],
                'register': dest_reg
            }
            
        # Variable doesn't exist
        return {'type': 'variable_not_found'}