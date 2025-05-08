"""
Linear Scanner for Penguin Language Compiler

This module implements a linear scan register allocation algorithm.
Linear scan is a simple but effective register allocation algorithm that
allocates registers to variables in a single pass through the code.
"""

from typing import Dict, List, Set, Tuple, Optional
from IRProgram import *
from LivenessAnalyzer import LivenessAnalyzer

class LiveRange:
    """Represents the live range of a variable."""
    
    def __init__(self, var_name: str, start: int, end: int):
        self.var_name = var_name  # Variable name
        self.start = start  # First instruction where variable is live
        self.end = end  # Last instruction where variable is live
        self.register = None  # Allocated register or None if spilled to memory
        self.spill_location = None  # Memory location if spilled
    
    def __lt__(self, other):
        """Comparison operator for sorting live ranges by start point."""
        return self.start < other.start
    
    def overlaps(self, other) -> bool:
        """Check if this live range overlaps with another."""
        return not (self.end < other.start or self.start > other.end)
    
    def __repr__(self):
        return f"LiveRange({self.var_name}, {self.start}-{self.end}, reg={self.register}, spill={self.spill_location})"


class LinearScanner:
    """
    Implements the linear scan register allocation algorithm.
    Linear scan is simpler than graph coloring but generally effective for register allocation.
    """
    
    def __init__(self, num_registers: int = 4):
        """
        Initialize the linear scanner.
        
        Args:
            num_registers: Number of available registers for allocation
        """
        self.num_registers = num_registers
        self.liveness_analyzer = LivenessAnalyzer()
        
        # Registers available on the GameBoy Z80 CPU
        # We'll use b, c, d, e, h, l as general purpose registers
        # a is often used for special operations
        self.registers = ['b', 'c', 'd', 'e', 'h', 'l']
        
        # Currently active ranges (being processed)
        self.active = []
        
        # Mapping from variable names to their allocated registers or spill locations
        self.allocation = {}
        
        # Counter for spill locations
        self.spill_counter = 0
        
        # Live ranges for all variables
        self.live_ranges = []
    
    def allocate_program(self, ir_program: IRProgram) -> Dict[str, Dict[str, str]]:
        """
        Allocate registers for all procedures in the program.
        
        Args:
            ir_program: The IR program to allocate registers for
            
        Returns:
            A dictionary mapping procedure names to allocation dictionaries
            (which map variable names to register names or spill locations)
        """
        result = {}
        
        # Analyze liveness for the entire program
        liveness_info = self.liveness_analyzer.analyze_program(ir_program)
        
        # Allocate registers for main section
        if ir_program.main_instructions:
            result["_global"] = self.allocate_procedure(
                "_global", ir_program.main_instructions, liveness_info["_global"])
        
        # Allocate registers for each procedure
        for proc_name, procedure in ir_program.procedures.items():
            result[proc_name] = self.allocate_procedure(
                proc_name, procedure.instructions, liveness_info[proc_name])
            
        return result
    
    def allocate_procedure(self, 
                        proc_name: str, 
                        instructions: List[IRInstruction], 
                        liveness_info: Dict[int, Set[str]]) -> Dict[str, str]:
        """
        Allocate registers for a single procedure.
        
        Args:
            proc_name: Name of the procedure
            instructions: The IR instructions in the procedure
            liveness_info: The liveness information for the procedure
            
        Returns:
            A dictionary mapping variable names to register names or spill locations
        """
        self.active = []
        self.allocation = {}
        self.spill_counter = 0
        
        # Find parameter variables by looking for IRArgLoad instructions
        param_vars = []
        for i, instr in enumerate(instructions):
            if isinstance(instr, IRArgLoad):
                param_vars.append((instr.dest, instr.arg_index))
        
        # Sort parameters by their argument index
        param_vars.sort(key=lambda x: x[1])
        
        # Allocate parameters to specific registers (b, c, d, e)
        register_order = ['b', 'c', 'd', 'e']
        for i, (param_var, _) in enumerate(param_vars):
            if i < len(register_order):
                self.allocation[param_var] = register_order[i]
        
        # Build live ranges from liveness information
        self.build_live_ranges(instructions, liveness_info)
        
        # Filter out parameters from live ranges to prevent them from being reallocated
        self.live_ranges = [lr for lr in self.live_ranges if lr.var_name not in self.allocation]
        
        # Sort live ranges by start point
        self.live_ranges.sort()
        
        # Adjust number of available registers
        original_num_registers = self.num_registers
        self.num_registers = original_num_registers - len(param_vars)
        
        # Perform linear scan with remaining registers
        self.linear_scan()
        
        # Restore original number of registers
        self.num_registers = original_num_registers
        
        return self.allocation
    
    def build_live_ranges(self, 
                         instructions: List[IRInstruction], 
                         liveness_info: Dict[int, Set[str]]) -> None:
        """
        Build live ranges for all variables in the procedure.
        
        Args:
            instructions: The IR instructions in the procedure
            liveness_info: The liveness information for the procedure
        """
        self.live_ranges = []
        
        # Find all variables in the procedure
        variables = set()
        for live_set in liveness_info.values():
            variables.update(live_set)
        
        # Determine live range for each variable
        for var in variables:
            start = float('inf')
            end = -1
            
            for i in range(len(instructions)):
                if var in liveness_info.get(i, set()):
                    start = min(start, i)
                    end = max(end, i)
            
            if start <= end:
                self.live_ranges.append(LiveRange(var, start, end))
    
    def linear_scan(self) -> None:
        """
        Perform linear scan register allocation.
        Processes live ranges in order of their start points.
        """
        for live_range in self.live_ranges:
            # Expire old intervals
            self.expire_old_intervals(live_range.start)
            
            if len(self.active) >= self.num_registers:
                # Need to spill either this or another live range
                self.handle_spill(live_range)
            else:
                # Allocate a free register
                reg = self.get_free_register()
                live_range.register = reg
                self.allocation[live_range.var_name] = reg
                
                # Add to active list
                self.active.append(live_range)
                # Sort active by end point
                self.active.sort(key=lambda lr: lr.end)
    
    def expire_old_intervals(self, position: int) -> None:
        """
        Expire intervals that end before the current position.
        
        Args:
            position: The current instruction position
        """
        i = 0
        while i < len(self.active):
            if self.active[i].end < position:
                # Expired, remove from active list
                self.active.pop(i)
            else:
                i += 1
    
    def handle_spill(self, live_range: LiveRange) -> None:
        """
        Handle the case when we need to spill a live range.
        Either spill the current range or the one with the furthest end point.
        
        Args:
            live_range: The current live range being processed
        """
        # Find the active live range with the furthest end point
        spill_candidate = self.active[-1]  # Last in active (sorted by end point)
        
        if spill_candidate.end > live_range.end:
            # Spill the candidate with later end point
            live_range.register = spill_candidate.register
            self.allocation[live_range.var_name] = spill_candidate.register
            
            # Spill the previous owner of this register
            spill_loc = self.get_spill_location()
            spill_candidate.register = None
            spill_candidate.spill_location = spill_loc
            self.allocation[spill_candidate.var_name] = spill_loc
            
            # Replace in active list
            self.active[-1] = live_range
            # Re-sort active by end point
            self.active.sort(key=lambda lr: lr.end)
        else:
            # Spill the current live range
            spill_loc = self.get_spill_location()
            live_range.register = None
            live_range.spill_location = spill_loc
            self.allocation[live_range.var_name] = spill_loc
    
    def get_free_register(self) -> str:
        """
        Get a free register that's not currently in use.
        
        Returns:
            A register name
        """
        used_regs = {lr.register for lr in self.active if lr.register is not None}
        for reg in self.registers:
            if reg not in used_regs:
                return reg
        
        # Should never reach here if we've handled spills correctly
        raise RuntimeError("No free registers found")
    
    def get_spill_location(self) -> str:
        """
        Get a new spill location in memory.
        
        Returns:
            A string representing a memory location
        """
        loc = f"[sp+{self.spill_counter}]"
        self.spill_counter += 1  # Increment by 1 byte (word size)
        return loc
    
    def is_register(self, allocation: str) -> bool:
        """
        Check if an allocation is a register (as opposed to a spill location).
        
        Args:
            allocation: The allocation string to check
            
        Returns:
            True if the allocation is a register, False if it's a spill location
        """
        return allocation in self.registers