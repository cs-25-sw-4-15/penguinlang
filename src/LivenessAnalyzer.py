"""
Liveness Analyzer for Penguin Language Compiler

This module analyzes the liveness of variables in the intermediate representation (IR)
to enable efficient register allocation.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Dict, List, Set, Tuple

from src.IRProgram import *

# logging
from src. logger import logger

class LivenessAnalyzer:
    """
    Analyzes the liveness of variables in the IR code.
    
    Liveness analysis determines which variables are "live" at each point in the program.
    A variable is live at a particular program point if its value may be read before 
    its next definition.
    """
    
    def __init__(self):
        self.cfg = {}  # Control flow graph: mapping from instruction index to list of successor indices
        self.instructions = []  # List of all instructions in the current procedure
        self.def_vars = []  # Variables defined at each instruction
        self.use_vars = []  # Variables used at each instruction
        self.live_in = []   # Variables live at entry to each instruction
        self.live_out = []  # Variables live at exit from each instruction
        self.leaders = set()  # Leaders (first instructions of basic blocks)
        self.proc_name = ""  # Current procedure name
    
    def analyze_program(self, ir_program: IRProgram) -> Dict[str, Dict[int, Set[str]]]:
        """
        Analyze liveness for all procedures in the program.
        
        Args:
            ir_program: The IR program to analyze
            
        Returns:
            A dictionary mapping procedure names to their liveness information
            (which maps instruction indices to sets of live variables)
        """
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
        """
        Analyze liveness for a set of instructions.
        
        Args:
            instructions: The list of IR instructions to analyze
            
        Returns:
            A dictionary mapping instruction indices to sets of live variables
        """
        if not instructions:
            return {}
            
        self.instructions = instructions
        self.identify_basic_blocks()
        self.build_cfg()
        self.initialize_def_use()
        self.compute_liveness()
        
        # Create the result dictionary mapping instruction indices to live_out sets
        result = {}
        for i in range(len(instructions)):
            result[i] = self.live_out[i]
            
        return result
    
    def identify_basic_blocks(self) -> None:
        """
        Identify the basic blocks in the instructions.
        A basic block is a sequence of instructions with:
        - One entry point (the first instruction)
        - One exit point (the last instruction)
        - No branching except at the last instruction
        """
        # First instruction is a leader
        if self.instructions:
            self.leaders.add(0)
        
        for i, instr in enumerate(self.instructions):
            # Labels are leaders
            if isinstance(instr, IRLabel):
                self.leaders.add(i)
                
            # Instructions following jumps are leaders
            if i > 0 and isinstance(self.instructions[i-1], (IRJump, IRCondJump, IRReturn)):
                self.leaders.add(i)
                
            # Target of jumps are leaders
            if isinstance(instr, (IRJump, IRCondJump)):
                # Find the target label's index
                if isinstance(instr, IRJump):
                    target_labels = [instr.label]
                else:
                    target_labels = [instr.true_label]
                    if instr.false_label:
                        target_labels.append(instr.false_label)
                
                for label in target_labels:
                    for j, other_instr in enumerate(self.instructions):
                        if isinstance(other_instr, IRLabel) and other_instr.name == label:
                            self.leaders.add(j)
                            break
    
    def build_cfg(self) -> None:
        """
        Build the control flow graph (CFG) for the instructions.
        The CFG represents the flow of control between basic blocks.
        """
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
                
                # If there's a false label, find it too
                if instr.false_label:
                    for j, other_instr in enumerate(self.instructions):
                        if isinstance(other_instr, IRLabel) and other_instr.name == instr.false_label:
                            self.cfg[i].append(j)
                            break
                else:
                    # If no explicit false label, control flows to the next instruction
                    if i + 1 < len(self.instructions):
                        self.cfg[i].append(i + 1)
            elif isinstance(instr, IRReturn):
                # Return has no successors in this procedure
                pass
            else:
                # For all other instructions, control flows to the next instruction
                if i + 1 < len(self.instructions):
                    self.cfg[i].append(i + 1)
    
    def initialize_def_use(self) -> None:
        """
        Initialize the def_vars and use_vars lists for each instruction.
        def_vars: variables defined (written to) by the instruction
        use_vars: variables used (read from) by the instruction
        """
        self.def_vars = [set() for _ in range(len(self.instructions))]
        self.use_vars = [set() for _ in range(len(self.instructions))]
        
        for i, instr in enumerate(self.instructions):
            self._analyze_instr_def_use(i, instr)
    
    def _analyze_instr_def_use(self, idx: int, instr: IRInstruction) -> None:
        """
        Analyze which variables are defined and used by a single instruction.
        
        Args:
            idx: The index of the instruction
            instr: The instruction to analyze
        """
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
            
        elif isinstance(instr, IRHardwareCall):
            for arg in instr.args:
                self._add_if_var(self.use_vars[idx], arg)
                
        elif isinstance(instr, IRArgLoad):
            self.def_vars[idx].add(instr.dest)
    
    def _add_if_var(self, var_set: Set[str], name: str) -> None:
        """
        Add a name to a set if it's a variable (not a constant or label).
        
        Args:
            var_set: The set to add to
            name: The name to add
        """
        if isinstance(name, str) and not name.isdigit() and not name.startswith('"') and not name.startswith("'"):
            var_set.add(name)
    
    def compute_liveness(self) -> None:
        """
        Compute the liveness information for all instructions.
        Uses an iterative algorithm to propagate liveness information
        backward through the control flow graph.
        """
        n = len(self.instructions)
        self.live_in = [set() for _ in range(n)]
        self.live_out = [set() for _ in range(n)]
        
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
                
                # Check if anything changed
                if new_live_in != self.live_in[i] or new_live_out != self.live_out[i]:
                    changed = True
                    self.live_in[i] = new_live_in
                    self.live_out[i] = new_live_out
    
    def get_live_ranges(self) -> Dict[str, Tuple[int, int]]:
        """
        Compute the live ranges for each variable.
        A live range is the span of instructions where a variable is live.
        
        Returns:
            A dictionary mapping variable names to their live ranges as (start, end) tuples
        """
        variables = set()
        for i in range(len(self.instructions)):
            variables.update(self.def_vars[i])
            variables.update(self.use_vars[i])
        
        ranges = {}
        for var in variables:
            # Find first and last occurrence of var in live_in or live_out
            start = float('inf')
            end = -1
            
            for i in range(len(self.instructions)):
                if var in self.def_vars[i] or var in self.use_vars[i] or var in self.live_in[i] or var in self.live_out[i]:
                    start = min(start, i)
                    end = max(end, i)
            
            if start <= end:
                ranges[var] = (start, end)
        
        return ranges
    
    def get_interference_graph(self) -> Dict[str, Set[str]]:
        """
        Compute the interference graph for variables.
        Two variables interfere if they are live at the same time.
        
        Returns:
            A dictionary mapping variable names to sets of variables they interfere with
        """
        variables = set()
        for i in range(len(self.instructions)):
            variables.update(self.def_vars[i])
            variables.update(self.use_vars[i])
        
        graph = {var: set() for var in variables}
        
        # Two variables interfere if one is live out at a point where the other is defined
        for i in range(len(self.instructions)):
            for var_def in self.def_vars[i]:
                for var_live in self.live_out[i]:
                    if var_def != var_live:
                        graph[var_def].add(var_live)
                        graph[var_live].add(var_def)
        
        return graph