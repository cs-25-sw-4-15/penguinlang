import os
import sys
from typing import Dict, List, Set

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.IRProgram import *
from src.LivenessAnalyzer import LivenessAnalyzer
from src.logger import logger


class LiveRange:
    
    def __init__(self, var_name: str, start: int, end: int):
        self.var_name = var_name 
        self.start = start 
        self.end = end 
        self.register = None 
        self.spill_location = None 
    
    def __lt__(self, other):
        
        return self.start < other.start
    
    def overlaps(self, other) -> bool:
        
        return not (self.end < other.start or self.start > other.end)
    
    def __repr__(self):

        return f"LiveRange({self.var_name}, {self.start}-{self.end}, reg={self.register}, spill={self.spill_location})"


class LinearScanner:
    
    def __init__(self, num_registers: int = 4):
        
        self.num_registers = num_registers
        self.liveness_analyzer = LivenessAnalyzer()
        
        self.registers = ['b', 'c', 'd', 'e', 'h', 'l']
        
        self.active = []
        
        self.allocation = {}
        
        self.spill_counter = 0
        
        self.live_ranges = []
    
    def allocate_program(self, ir_program: IRProgram) -> Dict[str, Dict[str, str]]:
        #Returns a mapping from procedures, that goes from variable names to registers
        result = {}
        
        liveness_info = self.liveness_analyzer.analyze_program(ir_program)
        
        if ir_program.main_instructions:
            result["_global"] = self.allocate_procedure(
                "_global", ir_program.main_instructions, liveness_info["_global"])
        
        for proc_name, procedure in ir_program.procedures.items():
            result[proc_name] = self.allocate_procedure(
                proc_name, procedure.instructions, liveness_info[proc_name])
            
        return result
    
    def allocate_procedure(self, proc_name: str, instructions: List[IRInstruction], liveness_info: Dict[int, Set[str]]) -> Dict[str, str]:
        
        self.active = []
        self.allocation = {}
        self.spill_counter = 0
        
        # Find parametre ved at finde IRArgLoad, som altid er i toppen af procedure
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
        
        self.build_live_ranges(instructions, liveness_info)
        
        self.live_ranges = [lr for lr in self.live_ranges if lr.var_name not in self.allocation]
        
        self.live_ranges.sort()
        
        original_num_registers = self.num_registers

        self.num_registers = original_num_registers - len(param_vars)
        
        self.linear_scan()
        
        self.num_registers = original_num_registers
        
        return self.allocation
    
    def build_live_ranges(self, instructions: List[IRInstruction], liveness_info: Dict[int, Set[str]]) -> None:
        
        self.live_ranges = []
        
        variables = set()
        for live_set in liveness_info.values():
            variables.update(live_set)
        
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
        
        for live_range in self.live_ranges:
            self.expire_old_intervals(live_range.start)
            
            if len(self.active) >= self.num_registers:
                self.handle_spill(live_range)
            else:
                reg = self.get_free_register()
                live_range.register = reg
                self.allocation[live_range.var_name] = reg
                
                self.active.append(live_range)
                # Sort active by end point
                self.active.sort(key=lambda lr: lr.end)
    
    def expire_old_intervals(self, position: int) -> None:
        i = 0
        while i < len(self.active):
            if self.active[i].end < position:
                # Expired, remove from active list
                self.active.pop(i)
            else:
                i += 1
    
    def handle_spill(self, live_range: LiveRange) -> None:
        
        # Live range with the furthest spill point is found
        spill_candidate = self.active[-1]
        
        if spill_candidate.end > live_range.end:
            # Spill the candidate with later end point
            live_range.register = spill_candidate.register
            self.allocation[live_range.var_name] = spill_candidate.register
            
            # Spill the previous owner of this register
            spill_loc = self.get_spill_location()
            spill_candidate.register = None
            spill_candidate.spill_location = spill_loc
            self.allocation[spill_candidate.var_name] = spill_loc
            
            self.active[-1] = live_range
            self.active.sort(key=lambda lr: lr.end)
        #Spill nuværende
        else:
            spill_loc = self.get_spill_location()
            live_range.register = None
            live_range.spill_location = spill_loc
            self.allocation[live_range.var_name] = spill_loc
    
    def get_free_register(self) -> str:
        
        used_regs = {lr.register for lr in self.active if lr.register is not None}
        for reg in self.registers:
            if reg not in used_regs:
                return reg
        
        # Hvis spills fungerer ender vi aldrig her
        raise RuntimeError("No free registers found")
    
    def get_spill_location(self) -> str:
        
        loc = f"[sp+{self.spill_counter}]"
        self.spill_counter += 1  # 1 = word size, altså 8 bit
        
        return loc
    
    def is_register(self, allocation: str) -> bool:
        
        return allocation in self.registers
