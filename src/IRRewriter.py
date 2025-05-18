"""IR Rewriter for Penguin Language Compiler

This module rewrites the intermediate representation (IR) to use allocated
registers and handle spilled variables.
"""

# Stdlib imports
import os
import sys
from typing import Dict, List, Optional

# Extend module paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Custom modules
from src.IRProgram import *
from src.logger import logger


class IRRewriter:
    """
    Rewrites the IR code to use register allocations and handle spilled variables.
    
    After register allocation, this class transforms the IR to:
    1. Replace variable references with register references
    2. Insert load/store instructions for spilled variables
    """
    
    def __init__(self):
        self.current_allocations = {}  # Current variable allocations for the procedure
        self.spill_slots = {}  # Maps spill locations to stack offsets
        self.next_spill_slot = 0  # Next available spill slot
        self.proc_name = ""  # Current procedure name
        self.is_register = None  # Function to check if an allocation is a register
        
    def rewrite_program(self, ir_program: IRProgram, allocations: Dict[str, Dict[str, str]]) -> IRProgram:
        """
        Rewrite an entire IR program to use register allocations.
        
        Args:
            ir_program: The original IR program
            allocations: Register allocations for each procedure
            
        Returns:
            A new IR program with register allocations applied
        """
        
        # Create a new IR program
        new_program = IRProgram()
        
        # Copy globals
        new_program.globals = ir_program.globals.copy()
        new_program.global_address = ir_program.global_address.copy()
        
        # Rewrite main section
        if ir_program.main_instructions:
            self.proc_name = "main"
            self.current_allocations = allocations.get("_global", {})
            self.spill_slots = {}
            self.next_spill_slot = 0
            
            rewritten_main = self.rewrite_instructions(ir_program.main_instructions)
            new_program.main_instructions = rewritten_main
        
        # Rewrite each procedure
        for proc_name, procedure in ir_program.procedures.items():
            self.proc_name = proc_name
            self.current_allocations = allocations.get(proc_name, {})
            self.spill_slots = {}
            self.next_spill_slot = 0
            
            # Create a new procedure with the same signature
            new_proc = IRProcedure(procedure.name, procedure.params.copy(), procedure.return_type)
            
            # Rewrite the procedure body
            rewritten_body = self.rewrite_instructions(procedure.instructions)
            new_proc.instructions = rewritten_body
            
            # Add the procedure to the new program
            new_program.add_procedure(new_proc)
        
        return new_program
    
    def set_is_register_fn(self, is_register_fn):
        """
        Set the function to check if an allocation is a register.
        
        Args:
            is_register_fn: A function that takes an allocation string and returns True if it's a register
        """
        
        self.is_register = is_register_fn
    
    def rewrite_instructions(self, instructions: List[IRInstruction]) -> List[IRInstruction]:  
        rewritten = []
        
        if any(not self._is_register(alloc) for alloc in self.current_allocations.values()):
            rewritten.extend(self._generate_prologue())
        
        for instr in instructions:
            rewritten_instrs = self._rewrite_instruction(instr)
            
            if isinstance(instr, IRReturn) and any(not self._is_register(alloc) for alloc in self.current_allocations.values()):
                rewritten.extend(self._generate_epilogue())
                
            rewritten.extend(rewritten_instrs)
        
        return rewritten
    
    def _rewrite_instruction(self, instr: IRInstruction) -> List[IRInstruction]:
        
        method_name = f"_rewrite_{instr.__class__.__name__}"
        rewrite_method = getattr(self, method_name, None)
        
        if rewrite_method:
            return rewrite_method(instr)
        else:
            # Default: just return the instruction unchanged
            return [instr]
    
    def _rewrite_IRAssign(self, instr: IRAssign) -> List[IRInstruction]:
        
        result = []
        
        dest_alloc = self._get_allocation(instr.dest)
        src_alloc = self._get_allocation(instr.src)
        
        if src_alloc and not self._is_register(src_alloc):
            temp_reg = 'a'  # Use accumulator as a temporary
            result.append(IRLoad(temp_reg, src_alloc))
            src_alloc = temp_reg
            
        elif not src_alloc:
            src_alloc = instr.src
        
        # Create the assignment
        if dest_alloc:
            if self._is_register(dest_alloc):
                result.append(IRAssign(dest_alloc, src_alloc))
            else:
                temp_reg = 'a' if src_alloc != 'a' else 'b'
                if src_alloc != temp_reg:
                    result.append(IRAssign(temp_reg, src_alloc))
                result.append(IRStore(dest_alloc, temp_reg))
                
        else:
            # Destination doesn't have an allocation - keep original
            result.append(instr)
        
        return result
    
    def _rewrite_IRBinaryOp(self, instr: IRBinaryOp) -> List[IRInstruction]: 
        result = []
        
        dest_alloc = self._get_allocation(instr.dest)
        left_alloc = self._get_allocation(instr.left)
        right_alloc = self._get_allocation(instr.right)
        
        if left_alloc and not self._is_register(left_alloc):
            temp_reg = 'a' 
            result.append(IRLoad(temp_reg, left_alloc))
            left_alloc = temp_reg
        elif not left_alloc:
            left_alloc = instr.left
        
        if right_alloc and not self._is_register(right_alloc):
            temp_reg = 'h'
            result.append(IRLoad(temp_reg, right_alloc))
            right_alloc = temp_reg
        elif not right_alloc:
            right_alloc = instr.right
        
        if dest_alloc:
            if self._is_register(dest_alloc):
                result.append(IRBinaryOp(instr.op, dest_alloc, left_alloc, right_alloc))
            else:
                temp_reg = 'l' 
                result.append(IRBinaryOp(instr.op, temp_reg, left_alloc, right_alloc))
                result.append(IRStore(dest_alloc, temp_reg))
                
        else:
            result.append(instr)
        
        return result
    
    def _rewrite_IRUnaryOp(self, instr: IRUnaryOp) -> List[IRInstruction]:
        
        result = []
        
        dest_alloc = self._get_allocation(instr.dest)
        operand_alloc = self._get_allocation(instr.operand)
        
        if operand_alloc and not self._is_register(operand_alloc):
            temp_reg = 'a' 
            result.append(IRLoad(temp_reg, operand_alloc))
            operand_alloc = temp_reg
        elif not operand_alloc:
            operand_alloc = instr.operand
        
        if dest_alloc:
            if self._is_register(dest_alloc):
                result.append(IRUnaryOp(instr.op, dest_alloc, operand_alloc))
            else:
                temp_reg = 'h'
                result.append(IRUnaryOp(instr.op, temp_reg, operand_alloc))
                result.append(IRStore(dest_alloc, temp_reg))
        else:
            result.append(instr)
        
        return result
    
    def _rewrite_IRConstant(self, instr: IRConstant) -> List[IRInstruction]:  

        result = []
        
        dest_alloc = self._get_allocation(instr.dest)
        
        if dest_alloc:
            if self._is_register(dest_alloc):
                result.append(IRConstant(dest_alloc, instr.value))
            else:
                temp_reg = 'a'
                result.append(IRConstant(temp_reg, instr.value))
                result.append(IRStore(dest_alloc, temp_reg))
        else:
            result.append(instr)
        
        return result
    
    def _rewrite_IRLoad(self, instr: IRLoad) -> List[IRInstruction]:
        
        result = []
        
        dest_alloc = self._get_allocation(instr.dest)
        addr_alloc = self._get_allocation(instr.addr)
        
        if addr_alloc and not self._is_register(addr_alloc):
            temp_reg = 'h'
            result.append(IRLoad(temp_reg, addr_alloc))
            addr_alloc = temp_reg
        elif not addr_alloc:
            addr_alloc = instr.addr
        
        if dest_alloc:
            if self._is_register(dest_alloc):
                result.append(IRLoad(dest_alloc, addr_alloc))
            else:
                temp_reg = 'a'
                result.append(IRLoad(temp_reg, addr_alloc))
                result.append(IRStore(dest_alloc, temp_reg))
        else:
            result.append(instr)
        
        return result
    
    def _rewrite_IRStore(self, instr: IRStore) -> List[IRInstruction]:
        
        result = []
        
        addr_alloc = self._get_allocation(instr.addr)
        value_alloc = self._get_allocation(instr.value)
        
        if addr_alloc and not self._is_register(addr_alloc):
            temp_reg = 'h' 
            result.append(IRLoad(temp_reg, addr_alloc))
            addr_alloc = temp_reg
        elif not addr_alloc:
            addr_alloc = instr.addr
        
        # Handle value
        if value_alloc and not self._is_register(value_alloc):
            temp_reg = 'a'
            result.append(IRLoad(temp_reg, value_alloc))
            value_alloc = temp_reg
        elif not value_alloc:
            value_alloc = instr.value
        
        result.append(IRStore(addr_alloc, value_alloc))
        
        return result
    
    def _rewrite_IRIndexedLoad(self, instr: IRIndexedLoad) -> List[IRInstruction]:
        
        result = []
        
        dest_alloc = self._get_allocation(instr.dest)
        base_alloc = self._get_allocation(instr.base)
        index_alloc = self._get_allocation(instr.index)
        
        if base_alloc and not self._is_register(base_alloc):
            temp_reg = 'h'
            result.append(IRLoad(temp_reg, base_alloc))
            base_alloc = temp_reg
        elif not base_alloc:
            base_alloc = instr.base
        
        if index_alloc and not self._is_register(index_alloc):
            temp_reg = 'l'
            result.append(IRLoad(temp_reg, index_alloc))
            index_alloc = temp_reg
        elif not index_alloc:
            index_alloc = instr.index
        
        if dest_alloc:
            if self._is_register(dest_alloc):
                result.append(IRIndexedLoad(dest_alloc, base_alloc, index_alloc))
            else:
                temp_reg = 'a'
                result.append(IRIndexedLoad(temp_reg, base_alloc, index_alloc))
                result.append(IRStore(dest_alloc, temp_reg))
        else:
            result.append(instr)
        
        return result
    
    def _rewrite_IRIndexedStore(self, instr: IRIndexedStore) -> List[IRInstruction]:
        
        result = []
        
        base_alloc = self._get_allocation(instr.base)
        index_alloc = self._get_allocation(instr.index)
        value_alloc = self._get_allocation(instr.value)
        
        if base_alloc and not self._is_register(base_alloc):
            temp_reg = 'h'
            result.append(IRLoad(temp_reg, base_alloc))
            base_alloc = temp_reg
        elif not base_alloc:
            base_alloc = instr.base
        
        if index_alloc and not self._is_register(index_alloc):
            temp_reg = 'l'
            result.append(IRLoad(temp_reg, index_alloc))
            index_alloc = temp_reg
        elif not index_alloc:
            index_alloc = instr.index

        if value_alloc and not self._is_register(value_alloc):
            temp_reg = 'a'
            result.append(IRLoad(temp_reg, value_alloc))
            value_alloc = temp_reg
        elif not value_alloc:
            value_alloc = instr.value
        
        result.append(IRIndexedStore(base_alloc, index_alloc, value_alloc))
        
        return result
    
    def _rewrite_IRCondJump(self, instr: IRCondJump) -> List[IRInstruction]:
        
        result = []
        
        cond_alloc = self._get_allocation(instr.condition)
        
        if cond_alloc and not self._is_register(cond_alloc):
            temp_reg = 'a'
            result.append(IRLoad(temp_reg, cond_alloc))
            cond_alloc = temp_reg
        elif not cond_alloc:
            cond_alloc = instr.condition
        
        if instr.false_label:
            result.append(IRCondJump(cond_alloc, instr.true_label, instr.false_label))
        else:
            result.append(IRCondJump(cond_alloc, instr.true_label))
        
        return result
    
    def _rewrite_IRCall(self, instr: IRCall) -> List[IRInstruction]:
        
        result = []
        
        new_args = []
        for arg in instr.args:
            arg_alloc = self._get_allocation(arg)
            
            if arg_alloc and not self._is_register(arg_alloc):
                temp_reg = self._get_temp_reg()
                result.append(IRLoad(temp_reg, arg_alloc))
                new_args.append(temp_reg)
            elif arg_alloc:
                new_args.append(arg_alloc)
            else:
                new_args.append(arg)
        
        dest_alloc = self._get_allocation(instr.dest) if instr.dest else None
        
        if dest_alloc:
            if self._is_register(dest_alloc):
                result.append(IRCall(instr.proc_name, new_args, dest_alloc))
            else:
                temp_reg = 'a'
                result.append(IRCall(instr.proc_name, new_args, temp_reg))
                result.append(IRStore(dest_alloc, temp_reg))
        else:
            result.append(IRCall(instr.proc_name, new_args, instr.dest))
        
        return result
    
    def _rewrite_IRReturn(self, instr: IRReturn) -> List[IRInstruction]:
        
        result = []
        
        if instr.value:
            value_alloc = self._get_allocation(instr.value)
            
            if value_alloc and not self._is_register(value_alloc):
                result.append(IRLoad('a', value_alloc))
                result.append(IRReturn('a'))
            elif value_alloc:
                result.append(IRReturn(value_alloc))
            else:
                result.append(instr)
        else:
            result.append(instr)
        
        return result
    
    def _rewrite_IRHardwareCall(self, instr: IRHardwareCall) -> List[IRInstruction]:
        
        result = []
        
        new_args = []
        for arg in instr.args:
            arg_alloc = self._get_allocation(arg)
            
            if arg_alloc and not self._is_register(arg_alloc):
                temp_reg = self._get_temp_reg()
                result.append(IRLoad(temp_reg, arg_alloc))
                new_args.append(temp_reg)
            elif arg_alloc:
                new_args.append(arg_alloc)
            else:
                new_args.append(arg)
        
        result.append(IRHardwareCall(instr.module, instr.function, new_args))
        
        return result
    
    def _rewrite_IRHardwareLoad(self, instr: IRHardwareLoad) -> List[IRInstruction]:
        
        result = []
        
        dest_alloc = self._get_allocation(instr.dest)
        
        if dest_alloc:
            if self._is_register(dest_alloc):
                result.append(IRHardwareLoad(dest_alloc, instr.register))
            else:
                temp_reg = 'a'
                result.append(IRHardwareLoad(temp_reg, instr.register))
                result.append(IRStore(dest_alloc, temp_reg))
        else:
            result.append(instr)
        
        return result
    
    def _rewrite_IRHardwareStore(self, instr: IRHardwareStore) -> List[IRInstruction]:
        
        result = []
        
        value_alloc = self._get_allocation(instr.value)
        
        if value_alloc and not self._is_register(value_alloc):
            temp_reg = 'a'
            result.append(IRLoad(temp_reg, value_alloc))
            result.append(IRHardwareStore(instr.register, temp_reg))
        elif value_alloc:
            result.append(IRHardwareStore(instr.register, value_alloc))
        else:
            result.append(instr)
        
        return result
    
    def _rewrite_IRHardwareIndexedLoad(self, instr: IRHardwareIndexedLoad) -> List[IRInstruction]:
        
        result = []
        
        dest_alloc = self._get_allocation(instr.dest)
        index_alloc = self._get_allocation(instr.index)
        
        if index_alloc and not self._is_register(index_alloc):
            temp_reg = 'h'
            result.append(IRLoad(temp_reg, index_alloc))
            index_alloc = temp_reg
        elif not index_alloc:
            index_alloc = instr.index
        
        if dest_alloc:
            if self._is_register(dest_alloc):
                result.append(IRHardwareIndexedLoad(dest_alloc, instr.register, index_alloc))
            else:
                temp_reg = 'a'
                result.append(IRHardwareIndexedLoad(temp_reg, instr.register, index_alloc))
                result.append(IRStore(dest_alloc, temp_reg))
        else:
            result.append(instr)
        
        return result
    
    def _rewrite_IRHardwareIndexedStore(self, instr: IRHardwareIndexedStore) -> List[IRInstruction]:
        
        result = []
        
        index_alloc = self._get_allocation(instr.index)
        value_alloc = self._get_allocation(instr.value)
        
        if index_alloc and not self._is_register(index_alloc):
            temp_reg = 'h'
            result.append(IRLoad(temp_reg, index_alloc))
            index_alloc = temp_reg
        elif not index_alloc:
            index_alloc = instr.index
        
        if value_alloc and not self._is_register(value_alloc):
            temp_reg = 'a'
            result.append(IRLoad(temp_reg, value_alloc))
            value_alloc = temp_reg
        elif not value_alloc:
            value_alloc = instr.value
        
        result.append(IRHardwareIndexedStore(instr.register, index_alloc, value_alloc))
        
        return result
    
    def _rewrite_IRHardwareIndexedDoubleLoad(self, instr: IRHardwareIndexedDoubleLoad) -> List[IRInstruction]:
        
        result = []
        
        dest_alloc = self._get_allocation(instr.dest)
        index_alloc = self._get_allocation(instr.index)
        index_alloc2 = self._get_allocation(instr.index2)
        
        if index_alloc and not self._is_register(index_alloc):
            temp_reg = 'h'
            result.append(IRLoad(temp_reg, index_alloc))
            index_alloc = temp_reg
        elif not index_alloc:
            index_alloc = instr.index

        # Handle index
        if index_alloc2 and not self._is_register(index_alloc2):
            temp_reg = 'l'
            result.append(IRLoad(temp_reg, index_alloc2))
            index_alloc2 = temp_reg
        elif not index_alloc2:
            index_alloc2 = instr.index
        
        if dest_alloc:
            if self._is_register(dest_alloc):
                result.append(IRHardwareIndexedDoubleLoad(dest_alloc, instr.register, index_alloc, index_alloc2))
            else:
                temp_reg = 'a'
                result.append(IRHardwareIndexedDoubleLoad(temp_reg, instr.register, index_alloc, index_alloc2))
                result.append(IRStore(dest_alloc, temp_reg))
        else:
            result.append(instr)
        
        return result
    
    def _rewrite_IRHardwareIndexedDoubleStore(self, instr: IRHardwareIndexedDoubleStore) -> List[IRInstruction]:
        
        result = []
        
        index_alloc = self._get_allocation(instr.index)
        index_alloc2 = self._get_allocation(instr.index2)
        value_alloc = self._get_allocation(instr.value)
        
        if index_alloc and not self._is_register(index_alloc):
            temp_reg = 'h'
            result.append(IRLoad(temp_reg, index_alloc))
            index_alloc = temp_reg
        elif not index_alloc:
            index_alloc = instr.index

        if index_alloc2 and not self._is_register(index_alloc2):
            temp_reg = 'l'
            result.append(IRLoad(temp_reg, index_alloc2))
            index_alloc2 = temp_reg
        elif not index_alloc2:
            index_alloc2 = instr.index
        
        if value_alloc and not self._is_register(value_alloc):
            temp_reg = 'a'
            result.append(IRLoad(temp_reg, value_alloc))
            value_alloc = temp_reg
        elif not value_alloc:
            value_alloc = instr.value
        
        result.append(IRHardwareIndexedDoubleStore(instr.register, index_alloc, index_alloc2, value_alloc))
        
        return result
    
    def _rewrite_IRLabel(self, instr: IRLabel) -> List[IRInstruction]:
        
        return [instr]
    
    def _rewrite_IRJump(self, instr: IRJump) -> List[IRInstruction]:
        
        return [instr]
    
    def _rewrite_IRArgLoad(self, instr: IRArgLoad) -> List[IRInstruction]:
        
        result = []
        
        dest_alloc = self._get_allocation(instr.dest)
        
        if dest_alloc:
            if self._is_register(dest_alloc):
                result.append(IRArgLoad(dest_alloc, instr.arg_index))
            else:
                temp_reg = 'a'
                result.append(IRArgLoad(temp_reg, instr.arg_index))
                result.append(IRStore(dest_alloc, temp_reg))
        else:
            result.append(instr)
        
        return result
    
    def _rewrite_IRIncBin(self, instr: IRIncBin) -> List[IRInstruction]:
        
        return [instr]
    
    def _rewrite_IRHardwareMemCpy(self, instr: IRHardwareMemCpy) -> List[IRInstruction]:
        
        return [instr]
    
    def _get_allocation(self, var_name: str) -> Optional[str]:
        
        if var_name in self.current_allocations:
            return self.current_allocations[var_name]
        return None
    
    def _is_register(self, allocation: str) -> bool:
        # TODO: HANDLE IF WE MODIFY HOW REGISTERS ARE IDENTIFIED, GOOD FOR NOW
        if self.is_register:
            return self.is_register(allocation)
        else:
            return allocation in ['a', 'b', 'c', 'd', 'e', 'h', 'l']
    
    def _get_temp_reg(self) -> str:
        # For now, this is probably fine
        return 'a'
    
    def _generate_prologue(self) -> List[IRInstruction]:
        
        result = []
        
        spill_slots = {}
        spill_count = 0
        
        for var, alloc in self.current_allocations.items():
            if not self._is_register(alloc):
                # Extract the offset from the allocation string ([sp+X])
                if '[sp+' in alloc:
                    offset = int(alloc.split('[sp+')[1].split(']')[0])
                    spill_slots[var] = offset
                    spill_count = max(spill_count, offset + 1)
        
        if spill_count > 0:
            result.append(IRChangeSP(spill_count, '-'))
        
        return result
    
    def _generate_epilogue(self) -> List[IRInstruction]:
        
        result = []
        
        spill_count = 0
        
        for var, alloc in self.current_allocations.items():
            if not self._is_register(alloc):
                if '[sp+' in alloc:
                    offset = int(alloc.split('[sp+')[1].split(']')[0])
                    spill_count = max(spill_count, offset + 1) 
        
        if spill_count > 0:
            result.append(IRChangeSP(spill_count, '+'))
        
        return result
