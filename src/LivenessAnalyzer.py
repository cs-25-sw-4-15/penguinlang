import os
import sys
from typing import Dict, List, Set, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.IRProgram import *
from src.logger import logger


class LivenessAnalyzer:
    
    def __init__(self):
        self.cfg = {} 
        self.instructions = []  
        self.def_vars = []  
        self.use_vars = [] 
        self.live_in = []   
        self.live_out = []  
        self.proc_name = "" 
    
    def analyze_program(self, ir_program: IRProgram) -> Dict[str, Dict[int, Set[str]]]:

        result = {}
        
        # Analyze main section
        if ir_program.main_instructions:
            self.proc_name = "_global"
            result["_global"] = self.analyze_instructions(ir_program.main_instructions)
        
        # Analyze each procedure
        for proc_name, procedure in ir_program.procedures.items():
            self.proc_name = proc_name
            result[proc_name] = self.analyze_instructions(procedure.instructions)
            
        return result
    
    def analyze_instructions(self, instructions: List[IRInstruction]) -> Dict[int, Set[str]]:
        
        if not instructions:
            return {}
            
        self.instructions = instructions
        self.build_cfg()
        self.initialize_def_use()
        self.compute_liveness()
        
        result = {}
        for i in range(len(instructions)):
            result[i] = self.live_out[i]
            
        return result
    
    def build_cfg(self) -> None:        
        # TODO: make less complex
        
        self.cfg = {i: [] for i in range(len(self.instructions))}
        
        for i, instr in enumerate(self.instructions):
            if isinstance(instr, IRJump):
                # Find the target label
                for j, other_instr in enumerate(self.instructions):
                    if isinstance(other_instr, IRLabel) and other_instr.name == instr.label:
                        self.cfg[i].append(j)
                        break
            elif isinstance(instr, IRCondJump):
                # Find the true target label
                for j, other_instr in enumerate(self.instructions):
                    if isinstance(other_instr, IRLabel) and other_instr.name == instr.true_label:
                        self.cfg[i].append(j)
                        break
                
                if instr.false_label:
                    for j, other_instr in enumerate(self.instructions):
                        if isinstance(other_instr, IRLabel) and other_instr.name == instr.false_label:
                            self.cfg[i].append(j)
                            break
                else:
                    if i + 1 < len(self.instructions):
                        self.cfg[i].append(i + 1)
            elif isinstance(instr, IRReturn):
                # Return has no successors in this procedure
                pass
            else:
                if i + 1 < len(self.instructions):
                    self.cfg[i].append(i + 1)
    
    def initialize_def_use(self) -> None:
        
        self.def_vars = [set() for _ in range(len(self.instructions))]
        self.use_vars = [set() for _ in range(len(self.instructions))]
        
        for i, instr in enumerate(self.instructions):
            self._analyze_instr_def_use(i, instr)
    
    def _analyze_instr_def_use(self, idx: int, instr: IRInstruction) -> None:
        # TODO: make less complex
        
        if isinstance(instr, IRAssign):
            self.def_vars[idx].add(instr.dest)
            self._add_if_var(self.use_vars[idx], instr.src)
            
        elif isinstance(instr, IRBinaryOp):
            self.def_vars[idx].add(instr.dest)
            self._add_if_var(self.use_vars[idx], instr.left)
            self._add_if_var(self.use_vars[idx], instr.right)
            
        elif isinstance(instr, IRUnaryOp):
            self.def_vars[idx].add(instr.dest)
            self._add_if_var(self.use_vars[idx], instr.operand)
            
        elif isinstance(instr, IRConstant):
            self.def_vars[idx].add(instr.dest)
            
        elif isinstance(instr, IRLoad):
            self.def_vars[idx].add(instr.dest)
            
        elif isinstance(instr, IRStore):
            self._add_if_var(self.use_vars[idx], instr.value)
            
        elif isinstance(instr, IRIndexedLoad):
            self.def_vars[idx].add(instr.dest)
            self._add_if_var(self.use_vars[idx], instr.index)
            
        elif isinstance(instr, IRIndexedStore):
            self._add_if_var(self.use_vars[idx], instr.index)
            self._add_if_var(self.use_vars[idx], instr.value)
            
        elif isinstance(instr, IRCondJump):
            self._add_if_var(self.use_vars[idx], instr.condition)
            
        elif isinstance(instr, IRCall):
            # All arguments are used
            for arg in instr.args:
                self._add_if_var(self.use_vars[idx], arg)
            
            # The destination is defined if it exists
            if instr.dest:
                self.def_vars[idx].add(instr.dest)
                
        elif isinstance(instr, IRReturn):
            if instr.value:
                self._add_if_var(self.use_vars[idx], instr.value)
                
        elif isinstance(instr, IRHardwareLoad):
            self.def_vars[idx].add(instr.dest)
            
        elif isinstance(instr, IRHardwareStore):
            self._add_if_var(self.use_vars[idx], instr.value)
            
        elif isinstance(instr, IRHardwareIndexedLoad):
            self.def_vars[idx].add(instr.dest)
            self._add_if_var(self.use_vars[idx], instr.index)
            
        elif isinstance(instr, IRHardwareIndexedStore):
            self._add_if_var(self.use_vars[idx], instr.index)
            self._add_if_var(self.use_vars[idx], instr.value)

        elif isinstance(instr, IRHardwareIndexedDoubleLoad):
            self.def_vars[idx].add(instr.dest)
            self._add_if_var(self.use_vars[idx], instr.index)
            self._add_if_var(self.use_vars[idx], instr.index2)
            
        elif isinstance(instr, IRHardwareIndexedDoubleStore):
            self._add_if_var(self.use_vars[idx], instr.index)
            self._add_if_var(self.use_vars[idx], instr.index2)
            self._add_if_var(self.use_vars[idx], instr.value)
            
        elif isinstance(instr, IRHardwareCall):
            for arg in instr.args:
                self._add_if_var(self.use_vars[idx], arg)
                
        elif isinstance(instr, IRArgLoad):
            self.def_vars[idx].add(instr.dest)
    
    def _add_if_var(self, var_set: Set[str], name: str) -> None:
        
        if isinstance(name, str) and not name.isdigit() and not name.startswith('"') and not name.startswith("'"):
            var_set.add(name)
    
    def compute_liveness(self) -> None:
        
        n = len(self.instructions)
        self.live_in = [set() for _ in range(n)]
        self.live_out = [set() for _ in range(n)]
        
        for i in range(n):
            self.live_out[i].update(self.def_vars[i])

        # Iterative algorithm to compute liveness
        changed = True
        while changed:
            changed = False
            
            # Iterate through instructions in reverse (bottom-up)
            for i in range(n - 1, -1, -1):
                # Compute new live_in for this instruction
                new_live_in = set(self.use_vars[i])
                new_live_in.update(self.live_out[i] - self.def_vars[i])
                
                # Compute new live_out for this instruction
                new_live_out = set()
                for succ in self.cfg[i]:
                    new_live_out.update(self.live_in[succ])

                new_live_out.update(self.def_vars[i])
                
                # Check if anything changed
                if new_live_in != self.live_in[i] or new_live_out != self.live_out[i]:
                    changed = True
                    self.live_in[i] = new_live_in
                    self.live_out[i] = new_live_out
    
