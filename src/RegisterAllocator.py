import os
import sys
from typing import Dict, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.IRProgram import *
from src.LinearScanner import LinearScanner
from src.IRRewriter import IRRewriter
from src.logger import logger
from src.logger import logger


class RegisterAllocator:
    
    def __init__(self, num_registers: int = 4):
        
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
        
        # Step 1 and 2: Perform liveness analysis (invoked by linearscanner.py) and linear scan register allocation
        logger.debug("Allocating registers with linear scan...")
        self.allocations = self.linear_scanner.allocate_program(ir_program)
        
        # Step 3: Calculate statistics
        self._calculate_stats()
        self._print_allocation_summary()
        
        # Step 4: Rewrite the IR program with register allocations
        logger.debug("Rewriting IR program with register allocations...")
        rewritten_program = self.ir_rewriter.rewrite_program(ir_program, self.allocations)
        
        return rewritten_program
    
    def _calculate_stats(self) -> None:
        
        total_vars = 0
        total_regs = 0
        total_spills = 0
        
        for proc_name, alloc in self.allocations.items():
            proc_vars = len(alloc)
            total_vars += proc_vars
            
            # Count register allocations vs spills
            proc_regs = sum(1 for var, loc in alloc.items() if self.linear_scanner.is_register(loc))
            proc_spills = proc_vars - proc_regs
            
            total_regs += proc_regs
            total_spills += proc_spills
            
            logger.debug(f"Procedure {proc_name}: {proc_vars} variables, " + f"{proc_regs} in registers, {proc_spills} spilled to memory")
        
        self.stats['variables'] = total_vars
        self.stats['registers_used'] = total_regs
        self.stats['spills'] = total_spills
    
    def _print_allocation_summary(self) -> None:
        
        logger.info("\nRegister Allocation Summary:")
        logger.info(f"Total variables: {self.stats['variables']}")
        logger.info(f"Variables in registers: {self.stats['registers_used']} " + f"({self.stats['registers_used']/max(1, self.stats['variables'])*100:.1f}%)")
        logger.info(f"Variables spilled to memory: {self.stats['spills']} " + f"({self.stats['spills']/max(1, self.stats['variables'])*100:.1f}%)")
        
        for proc_name, alloc in self.allocations.items():
            logger.debug(f"\nAllocation for {proc_name}:")
            
            by_location = {}
            for var, loc in alloc.items():
                if loc not in by_location:
                    by_location[loc] = []
                by_location[loc].append(var)
            
            for reg in self.linear_scanner.registers:
                if reg in by_location:
                    vars_in_reg = ", ".join(by_location[reg])
                    logger.debug(f"  Register {reg}: {vars_in_reg}")
            
            spill_locs = [loc for loc in by_location if loc not in self.linear_scanner.registers]
            if spill_locs:
                logger.debug("  Spill locations:")
                for loc in sorted(spill_locs):
                    vars_in_loc = ", ".join(by_location[loc])
                    logger.debug(f"    {loc}: {vars_in_loc}")
    
    def get_allocation(self, proc_name: str, var_name: str) -> Optional[str]:
        
        if proc_name in self.allocations and var_name in self.allocations[proc_name]:
            return self.allocations[proc_name][var_name]
        
        return None
    
    def is_register(self, allocation: str) -> bool:
        
        return self.linear_scanner.is_register(allocation)
    
    def get_all_register_allocations(self) -> Dict[str, Dict[str, str]]:
        
        return self.allocations
    
    def get_procedure_allocation(self, proc_name: str) -> Dict[str, str]:

        return self.allocations.get(proc_name, {})
    
    def get_statistics(self) -> Dict[str, int]:
        
        return self.stats
