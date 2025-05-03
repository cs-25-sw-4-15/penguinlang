"""
Register Allocator for Penguin Language Compiler

This module implements register allocation for the Penguin compiler,
interfacing between the liveness analysis, linear scanner, and IR rewriter.
"""

from typing import Dict, List, Set, Tuple, Optional
from IRProgram import IRInstruction, IRProgram, IRProcedure
from LivenessAnalyzer import LivenessAnalyzer
from LinearScanner import LinearScanner
from IRRewriter import IRRewriter

class RegisterAllocator:
    """
    Coordinates register allocation across the compilation process.
    
    This class brings together liveness analysis, linear scan allocation,
    and IR rewriting to perform register allocation for the entire program.
    """
    
    def __init__(self, num_registers: int = 6):
        """
        Initialize the register allocator.
        
        Args:
            num_registers: Number of available registers for allocation
        """
        self.liveness_analyzer = LivenessAnalyzer()
        self.linear_scanner = LinearScanner(num_registers)
        self.ir_rewriter = IRRewriter()
        
        # Mapping from procedure names to variable allocations
        self.allocations = {}
        
        # Statistics about register allocation
        self.stats = {
            'variables': 0,
            'registers_used': 0,
            'spills': 0
        }
    
    def allocate_registers(self, ir_program: IRProgram) -> IRProgram:
        """
        Allocate registers for an entire IR program.
        
        Args:
            ir_program: The IR program to allocate registers for
            
        Returns:
            A new IR program with register allocation applied
        """
        # Step 1: Perform liveness analysis
        print("Performing liveness analysis...")
        liveness_info = self.liveness_analyzer.analyze_program(ir_program)
        
        # Step 2: Perform linear scan register allocation
        print("Allocating registers with linear scan...")
        self.allocations = self.linear_scanner.allocate_program(ir_program)
        
        # Step 3: Calculate statistics
        self._calculate_stats()
        self._print_allocation_summary()
        
        # Step 4: Rewrite the IR program with register allocations
        print("Rewriting IR program with register allocations...")
        rewritten_program = self.ir_rewriter.rewrite_program(ir_program, self.allocations)
        
        return rewritten_program
    
    def _calculate_stats(self) -> None:
        """Calculate statistics about register allocation."""
        total_vars = 0
        total_regs = 0
        total_spills = 0
        
        for proc_name, alloc in self.allocations.items():
            proc_vars = len(alloc)
            total_vars += proc_vars
            
            # Count register allocations vs spills
            proc_regs = sum(1 for var, loc in alloc.items() 
                           if self.linear_scanner.is_register(loc))
            proc_spills = proc_vars - proc_regs
            
            total_regs += proc_regs
            total_spills += proc_spills
            
            print(f"Procedure {proc_name}: {proc_vars} variables, "
                  f"{proc_regs} in registers, {proc_spills} spilled to memory")
        
        self.stats['variables'] = total_vars
        self.stats['registers_used'] = total_regs
        self.stats['spills'] = total_spills
    
    def _print_allocation_summary(self) -> None:
        """Print a summary of the register allocation."""
        print("\nRegister Allocation Summary:")
        print(f"Total variables: {self.stats['variables']}")
        print(f"Variables in registers: {self.stats['registers_used']} "
              f"({self.stats['registers_used']/max(1, self.stats['variables'])*100:.1f}%)")
        print(f"Variables spilled to memory: {self.stats['spills']} "
              f"({self.stats['spills']/max(1, self.stats['variables'])*100:.1f}%)")
        
        # Print detailed allocation for each procedure
        for proc_name, alloc in self.allocations.items():
            print(f"\nAllocation for {proc_name}:")
            
            # Group by allocation location (register or memory)
            by_location = {}
            for var, loc in alloc.items():
                if loc not in by_location:
                    by_location[loc] = []
                by_location[loc].append(var)
            
            # Print registers first
            for reg in self.linear_scanner.registers:
                if reg in by_location:
                    vars_in_reg = ", ".join(by_location[reg])
                    print(f"  Register {reg}: {vars_in_reg}")
            
            # Then print spill locations
            spill_locs = [loc for loc in by_location if loc not in self.linear_scanner.registers]
            if spill_locs:
                print("  Spill locations:")
                for loc in sorted(spill_locs):
                    vars_in_loc = ", ".join(by_location[loc])
                    print(f"    {loc}: {vars_in_loc}")
    
    def get_allocation(self, proc_name: str, var_name: str) -> Optional[str]:
        """
        Get the allocation (register or memory location) for a variable.
        
        Args:
            proc_name: The name of the procedure containing the variable
            var_name: The name of the variable
            
        Returns:
            The register or memory location, or None if not allocated
        """
        if proc_name in self.allocations and var_name in self.allocations[proc_name]:
            return self.allocations[proc_name][var_name]
        return None
    
    def is_register(self, allocation: str) -> bool:
        """
        Check if an allocation is a register (as opposed to a spill location).
        
        Args:
            allocation: The allocation string to check
            
        Returns:
            True if the allocation is a register, False if it's a spill location
        """
        return self.linear_scanner.is_register(allocation)
    
    def get_all_register_allocations(self) -> Dict[str, Dict[str, str]]:
        """
        Get all register allocations for the program.
        
        Returns:
            A dictionary mapping procedure names to allocation dictionaries
        """
        return self.allocations
    
    def get_procedure_allocation(self, proc_name: str) -> Dict[str, str]:
        """
        Get register allocations for a specific procedure.
        
        Args:
            proc_name: The name of the procedure
            
        Returns:
            A dictionary mapping variable names to register or memory locations
        """
        return self.allocations.get(proc_name, {})
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get statistics about register allocation.
        
        Returns:
            A dictionary with statistics about the allocation
        """
        return self.stats