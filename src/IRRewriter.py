"""
IR Rewriter for Penguin Language Compiler

This module rewrites the intermediate representation (IR) to use allocated
registers and handle spilled variables.
"""

from typing import Dict, List, Set, Tuple, Optional
from IRProgram import IRInstruction, IRProgram, IRProcedure
from IRProgram import (
    IRAssign, IRBinaryOp, IRCall, IRCondJump, IRConstant, IRJump, IRLabel,
    IRLoad, IRReturn, IRStore, IRUnaryOp, IRIndexedLoad, IRIndexedStore,
    IRHardwareCall, IRHardwareRead, IRHardwareWrite, IRArgLoad,
    IRHardwareIndexedRead, IRHardwareIndexedWrite, IRIncBin, IRHardwareMemCpy
)

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
        
    def rewrite_program(self, 
                       ir_program: IRProgram, 
                       allocations: Dict[str, Dict[str, str]]) -> IRProgram:
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
        """
        Rewrite a list of IR instructions to use register allocations.
        
        Args:
            instructions: The original IR instructions
            
        Returns:
            A list of rewritten IR instructions
        """
        rewritten = []
        
        # Add prologue for spill slots if needed
        if any(not self._is_register(alloc) for alloc in self.current_allocations.values()):
            rewritten.extend(self._generate_prologue())
        
        # Rewrite each instruction
        for instr in instructions:
            rewritten_instrs = self._rewrite_instruction(instr)
            rewritten.extend(rewritten_instrs)
        
        # Add epilogue for spill slots if needed
        if any(not self._is_register(alloc) for alloc in self.current_allocations.values()):
            rewritten.extend(self._generate_epilogue())
        
        return rewritten
    
    def _rewrite_instruction(self, instr: IRInstruction) -> List[IRInstruction]:
        """
        Rewrite a single IR instruction to use register allocations.
        
        Args:
            instr: The original IR instruction
            
        Returns:
            A list of rewritten IR instructions (may be more than one if spill handling is needed)
        """
        method_name = f"_rewrite_{instr.__class__.__name__}"
        rewrite_method = getattr(self, method_name, None)
        
        if rewrite_method:
            return rewrite_method(instr)
        else:
            # Default: just return the instruction unchanged
            return [instr]
    
    def _rewrite_IRAssign(self, instr: IRAssign) -> List[IRInstruction]:
        """Rewrite an IRAssign instruction."""
        result = []
        
        # Get allocations
        dest_alloc = self._get_allocation(instr.dest)
        src_alloc = self._get_allocation(instr.src)
        
        # Check if we need to load from a spill slot
        if src_alloc and not self._is_register(src_alloc):
            # Load from spill slot to a temporary register
            temp_reg = 'a'  # Use accumulator as a temporary
            result.append(IRLoad(temp_reg, src_alloc))
            src_alloc = temp_reg
        elif not src_alloc:
            # Source is a constant or direct reference
            src_alloc = instr.src
        
        # Create the assignment
        if dest_alloc:
            if self._is_register(dest_alloc):
                # Assign directly to register
                result.append(IRAssign(dest_alloc, src_alloc))
            else:
                # Store to spill slot
                temp_reg = 'a' if src_alloc != 'a' else 'b'
                if src_alloc != temp_reg:
                    result.append(IRAssign(temp_reg, src_alloc))
                result.append(IRStore(dest_alloc, temp_reg))
        else:
            # Destination doesn't have an allocation - keep original
            result.append(instr)
        
        return result
    
    def _rewrite_IRBinaryOp(self, instr: IRBinaryOp) -> List[IRInstruction]:
        """Rewrite an IRBinaryOp instruction."""
        result = []
        
        # Get allocations
        dest_alloc = self._get_allocation(instr.dest)
        left_alloc = self._get_allocation(instr.left)
        right_alloc = self._get_allocation(instr.right)
        
        # Handle left operand
        if left_alloc and not self._is_register(left_alloc):
            # Load from spill slot to a temporary register
            temp_reg = 'a'  # Use accumulator for left operand
            result.append(IRLoad(temp_reg, left_alloc))
            left_alloc = temp_reg
        elif not left_alloc:
            left_alloc = instr.left
        
        # Handle right operand
        if right_alloc and not self._is_register(right_alloc):
            # Load from spill slot to a different temporary register
            temp_reg = 'b'  # Use b for right operand
            result.append(IRLoad(temp_reg, right_alloc))
            right_alloc = temp_reg
        elif not right_alloc:
            right_alloc = instr.right
        
        # Create the binary operation
        if dest_alloc:
            if self._is_register(dest_alloc):
                # Perform operation directly to register
                result.append(IRBinaryOp(instr.op, dest_alloc, left_alloc, right_alloc))
            else:
                # Perform operation to a temporary, then store
                temp_reg = 'c'  # Use c for result
                result.append(IRBinaryOp(instr.op, temp_reg, left_alloc, right_alloc))
                result.append(IRStore(dest_alloc, temp_reg))
        else:
            # No allocation for destination - keep original
            result.append(instr)
        
        return result
    
    def _rewrite_IRUnaryOp(self, instr: IRUnaryOp) -> List[IRInstruction]:
        """Rewrite an IRUnaryOp instruction."""
        result = []
        
        # Get allocations
        dest_alloc = self._get_allocation(instr.dest)
        operand_alloc = self._get_allocation(instr.operand)
        
        # Handle operand
        if operand_alloc and not self._is_register(operand_alloc):
            # Load from spill slot to a temporary register
            temp_reg = 'a'  # Use accumulator for operand
            result.append(IRLoad(temp_reg, operand_alloc))
            operand_alloc = temp_reg
        elif not operand_alloc:
            operand_alloc = instr.operand
        
        # Create the unary operation
        if dest_alloc:
            if self._is_register(dest_alloc):
                # Perform operation directly to register
                result.append(IRUnaryOp(instr.op, dest_alloc, operand_alloc))
            else:
                # Perform operation to a temporary, then store
                temp_reg = 'b'  # Use b for result
                result.append(IRUnaryOp(instr.op, temp_reg, operand_alloc))
                result.append(IRStore(dest_alloc, temp_reg))
        else:
            # No allocation for destination - keep original
            result.append(instr)
        
        return result
    
    def _rewrite_IRConstant(self, instr: IRConstant) -> List[IRInstruction]:
        """Rewrite an IRConstant instruction."""
        result = []
        
        # Get allocation for destination
        dest_alloc = self._get_allocation(instr.dest)
        
        if dest_alloc:
            if self._is_register(dest_alloc):
                # Assign constant directly to register
                result.append(IRConstant(dest_alloc, instr.value))
            else:
                # Load constant to a temporary, then store
                temp_reg = 'a'
                result.append(IRConstant(temp_reg, instr.value))
                result.append(IRStore(dest_alloc, temp_reg))
        else:
            # No allocation for destination - keep original
            result.append(instr)
        
        return result
    
    def _rewrite_IRLoad(self, instr: IRLoad) -> List[IRInstruction]:
        """Rewrite an IRLoad instruction."""
        result = []
        
        # Get allocations
        dest_alloc = self._get_allocation(instr.dest)
        addr_alloc = self._get_allocation(instr.addr)
        
        # Handle address
        if addr_alloc and not self._is_register(addr_alloc):
            # Load from spill slot to a temporary register
            temp_reg = 'b'  # Use b for address
            result.append(IRLoad(temp_reg, addr_alloc))
            addr_alloc = temp_reg
        elif not addr_alloc:
            addr_alloc = instr.addr
        
        # Create the load
        if dest_alloc:
            if self._is_register(dest_alloc):
                # Load directly to register
                result.append(IRLoad(dest_alloc, addr_alloc))
            else:
                # Load to a temporary, then store
                temp_reg = 'a'
                result.append(IRLoad(temp_reg, addr_alloc))
                result.append(IRStore(dest_alloc, temp_reg))
        else:
            # No allocation for destination - keep original
            result.append(instr)
        
        return result
    
    def _rewrite_IRStore(self, instr: IRStore) -> List[IRInstruction]:
        """Rewrite an IRStore instruction."""
        result = []
        
        # Get allocations
        addr_alloc = self._get_allocation(instr.addr)
        value_alloc = self._get_allocation(instr.value)
        
        # Handle address
        if addr_alloc and not self._is_register(addr_alloc):
            # Load from spill slot to a temporary register
            temp_reg = 'b'  # Use b for address
            result.append(IRLoad(temp_reg, addr_alloc))
            addr_alloc = temp_reg
        elif not addr_alloc:
            addr_alloc = instr.addr
        
        # Handle value
        if value_alloc and not self._is_register(value_alloc):
            # Load from spill slot to a temporary register
            temp_reg = 'a'  # Use a for value
            result.append(IRLoad(temp_reg, value_alloc))
            value_alloc = temp_reg
        elif not value_alloc:
            value_alloc = instr.value
        
        # Create the store
        result.append(IRStore(addr_alloc, value_alloc))
        
        return result
    
    def _rewrite_IRIndexedLoad(self, instr: IRIndexedLoad) -> List[IRInstruction]:
        """Rewrite an IRIndexedLoad instruction."""
        result = []
        
        # Get allocations
        dest_alloc = self._get_allocation(instr.dest)
        base_alloc = self._get_allocation(instr.base)
        index_alloc = self._get_allocation(instr.index)
        
        # Handle base
        if base_alloc and not self._is_register(base_alloc):
            # Load from spill slot to a temporary register
            temp_reg = 'b'
            result.append(IRLoad(temp_reg, base_alloc))
            base_alloc = temp_reg
        elif not base_alloc:
            base_alloc = instr.base
        
        # Handle index
        if index_alloc and not self._is_register(index_alloc):
            # Load from spill slot to a temporary register
            temp_reg = 'c'
            result.append(IRLoad(temp_reg, index_alloc))
            index_alloc = temp_reg
        elif not index_alloc:
            index_alloc = instr.index
        
        # Create the indexed load
        if dest_alloc:
            if self._is_register(dest_alloc):
                # Load directly to register
                result.append(IRIndexedLoad(dest_alloc, base_alloc, index_alloc))
            else:
                # Load to a temporary, then store
                temp_reg = 'a'
                result.append(IRIndexedLoad(temp_reg, base_alloc, index_alloc))
                result.append(IRStore(dest_alloc, temp_reg))
        else:
            # No allocation for destination - keep original
            result.append(instr)
        
        return result
    
    def _rewrite_IRIndexedStore(self, instr: IRIndexedStore) -> List[IRInstruction]:
        """Rewrite an IRIndexedStore instruction."""
        result = []
        
        # Get allocations
        base_alloc = self._get_allocation(instr.base)
        index_alloc = self._get_allocation(instr.index)
        value_alloc = self._get_allocation(instr.value)
        
        # Handle base
        if base_alloc and not self._is_register(base_alloc):
            temp_reg = 'b'
            result.append(IRLoad(temp_reg, base_alloc))
            base_alloc = temp_reg
        elif not base_alloc:
            base_alloc = instr.base
        
        # Handle index
        if index_alloc and not self._is_register(index_alloc):
            temp_reg = 'c'
            result.append(IRLoad(temp_reg, index_alloc))
            index_alloc = temp_reg
        elif not index_alloc:
            index_alloc = instr.index
        
        # Handle value
        if value_alloc and not self._is_register(value_alloc):
            temp_reg = 'a'
            result.append(IRLoad(temp_reg, value_alloc))
            value_alloc = temp_reg
        elif not value_alloc:
            value_alloc = instr.value
        
        # Create the indexed store
        result.append(IRIndexedStore(base_alloc, index_alloc, value_alloc))
        
        return result
    
    def _rewrite_IRCondJump(self, instr: IRCondJump) -> List[IRInstruction]:
        """Rewrite an IRCondJump instruction."""
        result = []
        
        # Get allocation for condition
        cond_alloc = self._get_allocation(instr.condition)
        
        # Handle condition
        if cond_alloc and not self._is_register(cond_alloc):
            # Load from spill slot to a temporary register
            temp_reg = 'a'
            result.append(IRLoad(temp_reg, cond_alloc))
            cond_alloc = temp_reg
        elif not cond_alloc:
            cond_alloc = instr.condition
        
        # Create the conditional jump
        if instr.false_label:
            result.append(IRCondJump(cond_alloc, instr.true_label, instr.false_label))
        else:
            result.append(IRCondJump(cond_alloc, instr.true_label))
        
        return result
    
    def _rewrite_IRCall(self, instr: IRCall) -> List[IRInstruction]:
        """Rewrite an IRCall instruction."""
        result = []
        
        # Process arguments
        new_args = []
        for arg in instr.args:
            arg_alloc = self._get_allocation(arg)
            
            if arg_alloc and not self._is_register(arg_alloc):
                # Load argument from spill slot to a temporary
                temp_reg = self._get_temp_reg()
                result.append(IRLoad(temp_reg, arg_alloc))
                new_args.append(temp_reg)
            elif arg_alloc:
                new_args.append(arg_alloc)
            else:
                new_args.append(arg)
        
        # Get allocation for destination
        dest_alloc = self._get_allocation(instr.dest) if instr.dest else None
        
        # Create the call
        if dest_alloc:
            if self._is_register(dest_alloc):
                # Call with result directly to register
                result.append(IRCall(instr.proc_name, new_args, dest_alloc))
            else:
                # Call with result to a temporary, then store
                temp_reg = 'a'
                result.append(IRCall(instr.proc_name, new_args, temp_reg))
                result.append(IRStore(dest_alloc, temp_reg))
        else:
            # Call with original destination or no destination
            result.append(IRCall(instr.proc_name, new_args, instr.dest))
        
        return result
    
    def _rewrite_IRReturn(self, instr: IRReturn) -> List[IRInstruction]:
        """Rewrite an IRReturn instruction."""
        result = []
        
        if instr.value:
            # Get allocation for return value
            value_alloc = self._get_allocation(instr.value)
            
            if value_alloc and not self._is_register(value_alloc):
                # Load return value from spill slot to accumulator (a)
                result.append(IRLoad('a', value_alloc))
                result.append(IRReturn('a'))
            elif value_alloc:
                result.append(IRReturn(value_alloc))
            else:
                result.append(instr)
        else:
            # Return with no value
            result.append(instr)
        
        return result
    
    def _rewrite_IRHardwareCall(self, instr: IRHardwareCall) -> List[IRInstruction]:
        """Rewrite an IRHardwareCall instruction."""
        result = []
        
        # Process arguments
        new_args = []
        for arg in instr.args:
            arg_alloc = self._get_allocation(arg)
            
            if arg_alloc and not self._is_register(arg_alloc):
                # Load argument from spill slot to a temporary
                temp_reg = self._get_temp_reg()
                result.append(IRLoad(temp_reg, arg_alloc))
                new_args.append(temp_reg)
            elif arg_alloc:
                new_args.append(arg_alloc)
            else:
                new_args.append(arg)
        
        # Create the hardware call
        result.append(IRHardwareCall(instr.module, instr.function, new_args))
        
        return result
    
    def _rewrite_IRHardwareRead(self, instr: IRHardwareRead) -> List[IRInstruction]:
        """Rewrite an IRHardwareRead instruction."""
        result = []
        
        # Get allocation for destination
        dest_alloc = self._get_allocation(instr.dest)
        
        if dest_alloc:
            if self._is_register(dest_alloc):
                # Read directly to register
                result.append(IRHardwareRead(dest_alloc, instr.register))
            else:
                # Read to a temporary, then store
                temp_reg = 'a'
                result.append(IRHardwareRead(temp_reg, instr.register))
                result.append(IRStore(dest_alloc, temp_reg))
        else:
            # No allocation for destination - keep original
            result.append(instr)
        
        return result
    
    def _rewrite_IRHardwareWrite(self, instr: IRHardwareWrite) -> List[IRInstruction]:
        """Rewrite an IRHardwareWrite instruction."""
        result = []
        
        # Get allocation for value
        value_alloc = self._get_allocation(instr.value)
        
        if value_alloc and not self._is_register(value_alloc):
            # Load value from spill slot to a temporary
            temp_reg = 'a'
            result.append(IRLoad(temp_reg, value_alloc))
            result.append(IRHardwareWrite(instr.register, temp_reg))
        elif value_alloc:
            result.append(IRHardwareWrite(instr.register, value_alloc))
        else:
            # No allocation for value - keep original
            result.append(instr)
        
        return result
    
    def _rewrite_IRHardwareIndexedRead(self, instr: IRHardwareIndexedRead) -> List[IRInstruction]:
        """Rewrite an IRHardwareIndexedRead instruction."""
        result = []
        
        # Get allocations
        dest_alloc = self._get_allocation(instr.dest)
        index_alloc = self._get_allocation(instr.index)
        
        # Handle index
        if index_alloc and not self._is_register(index_alloc):
            # Load from spill slot to a temporary register
            temp_reg = 'b'
            result.append(IRLoad(temp_reg, index_alloc))
            index_alloc = temp_reg
        elif not index_alloc:
            index_alloc = instr.index
        
        # Create the hardware indexed read
        if dest_alloc:
            if self._is_register(dest_alloc):
                # Read directly to register
                result.append(IRHardwareIndexedRead(dest_alloc, instr.register, index_alloc))
            else:
                # Read to a temporary, then store
                temp_reg = 'a'
                result.append(IRHardwareIndexedRead(temp_reg, instr.register, index_alloc))
                result.append(IRStore(dest_alloc, temp_reg))
        else:
            # No allocation for destination - keep original
            result.append(instr)
        
        return result
    
    def _rewrite_IRHardwareIndexedWrite(self, instr: IRHardwareIndexedWrite) -> List[IRInstruction]:
        """Rewrite an IRHardwareIndexedWrite instruction."""
        result = []
        
        # Get allocations
        index_alloc = self._get_allocation(instr.index)
        value_alloc = self._get_allocation(instr.value)
        
        # Handle index
        if index_alloc and not self._is_register(index_alloc):
            # Load from spill slot to a temporary register
            temp_reg = 'b'
            result.append(IRLoad(temp_reg, index_alloc))
            index_alloc = temp_reg
        elif not index_alloc:
            index_alloc = instr.index
        
        # Handle value
        if value_alloc and not self._is_register(value_alloc):
            # Load from spill slot to a temporary register
            temp_reg = 'a'
            result.append(IRLoad(temp_reg, value_alloc))
            value_alloc = temp_reg
        elif not value_alloc:
            value_alloc = instr.value
        
        # Create the hardware indexed write
        result.append(IRHardwareIndexedWrite(instr.register, index_alloc, value_alloc))
        
        return result
    
    def _rewrite_IRLabel(self, instr: IRLabel) -> List[IRInstruction]:
        """Labels don't need rewriting."""
        return [instr]
    
    def _rewrite_IRJump(self, instr: IRJump) -> List[IRInstruction]:
        """Jumps don't need rewriting."""
        return [instr]
    
    def _rewrite_IRArgLoad(self, instr: IRArgLoad) -> List[IRInstruction]:
        """Rewrite an IRArgLoad instruction."""
        result = []
        
        # Get allocation for destination
        dest_alloc = self._get_allocation(instr.dest)
        
        if dest_alloc:
            if self._is_register(dest_alloc):
                # Load argument directly to register
                result.append(IRArgLoad(dest_alloc, instr.arg_index))
            else:
                # Load argument to a temporary, then store
                temp_reg = 'a'
                result.append(IRArgLoad(temp_reg, instr.arg_index))
                result.append(IRStore(dest_alloc, temp_reg))
        else:
            # No allocation for destination - keep original
            result.append(instr)
        
        return result
    
    def _rewrite_IRIncBin(self, instr: IRIncBin) -> List[IRInstruction]:
        """IRIncBin doesn't need rewriting."""
        return [instr]
    
    def _rewrite_IRHardwareMemCpy(self, instr: IRHardwareMemCpy) -> List[IRInstruction]:
        """IRHardwareMemCpy doesn't need rewriting."""
        return [instr]
    
    def _get_allocation(self, var_name: str) -> Optional[str]:
        """Get the allocation (register or memory location) for a variable."""
        if var_name in self.current_allocations:
            return self.current_allocations[var_name]
        return None
    
    def _is_register(self, allocation: str) -> bool:
        """Check if an allocation is a register."""
        if self.is_register:
            return self.is_register(allocation)
        else:
            # Default implementation if no function is provided
            return allocation in ['a', 'b', 'c', 'd', 'e', 'h', 'l']
    
    def _get_temp_reg(self) -> str:
        """Get a temporary register for spill handling."""
        # For simplicity, always use the accumulator (a) as a temporary
        # In a real implementation, you would need to choose registers more carefully
        return 'a'
    
    def _generate_prologue(self) -> List[IRInstruction]:
        """Generate prologue code for allocating spill slots on the stack."""
        result = []
        
        # Count the number of spill slots needed
        spill_slots = {}
        spill_count = 0
        
        for var, alloc in self.current_allocations.items():
            if not self._is_register(alloc):
                # Extract the offset from the allocation string ([sp+X])
                if '[sp+' in alloc:
                    offset = int(alloc.split('[sp+')[1].split(']')[0])
                    spill_slots[var] = offset
                    spill_count = max(spill_count, offset + 2)  # +2 for word size
        
        if spill_count > 0:
            # Generate code to allocate space on the stack
            result.append(IRLabel(f"{self.proc_name}_prologue"))
            result.append(IRBinaryOp('-', 'sp', 'sp', str(spill_count)))
        
        return result
    
    def _generate_epilogue(self) -> List[IRInstruction]:
        """Generate epilogue code for deallocating spill slots from the stack."""
        result = []
        
        # Count the number of spill slots used
        spill_count = 0
        
        for var, alloc in self.current_allocations.items():
            if not self._is_register(alloc):
                # Extract the offset from the allocation string ([sp+X])
                if '[sp+' in alloc:
                    offset = int(alloc.split('[sp+')[1].split(']')[0])
                    spill_count = max(spill_count, offset + 2)  # +2 for word size
        
        if spill_count > 0:
            # Generate code to deallocate space from the stack
            result.append(IRLabel(f"{self.proc_name}_epilogue"))
            result.append(IRBinaryOp('+', 'sp', 'sp', str(spill_count)))
        
        return result