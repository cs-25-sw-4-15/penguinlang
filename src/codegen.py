""" Code Generation for the Penguin Compiler

Generates assembly code from an IR program.
"""

# Stdlib imports
import os
import sys

# Extend module paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Custom modules
from src.IRProgram import *
from src.codegenRegisters import *
from src.logger import logger


class CodeGenerator:

    def __init__(self):
        """
        Initialize the code generator.
        """
        
        self.variable_address_dict = {}
        self.cmp_counter = 0
        self.registerDict = codegenRegister()
        self.include_binaries = []

    def generate_code(self, ir_program: IRProgram) -> str:
        """
        Generate assembly code from an IR program.
        
        Args:
            ir_program: The IR program to generate code for
            
        Returns:
            A string containing the generated assembly code
        """
        
        self.variable_address_dict = ir_program.global_address
        # Initialize the assembly code string
        assembly_code = ""
        
        assembly_code += self.header()

        assembly_code += "PenguinEntry:\n"
        assembly_code += "ld sp, $DFFF\n"

        # Iterate over each instruction in the IR program
        for instruction in ir_program.main_instructions:
            # Convert the instruction to assembly code
            assembly_line = self.generate(instruction)
            
            # Append the assembly line to the code string
            if assembly_line:
                assembly_code += assembly_line + "\n"

        for procedure in ir_program.procedures.items():
            # add label for procedure
            assembly_code += f"Label{procedure[0]}:\n"
            
            for instruction in procedure[1].instructions:
                assembly_line = self.generate(instruction)
                
                if assembly_line:
                    assembly_code += assembly_line
            
        assembly_code += self.footer()

        total_binaries = "\n".join(self.include_binaries)
        assembly_code += total_binaries

        return assembly_code

    def header(self) -> str:
        """
        Generate the header for the assembly code.
        
        Returns:
            A string containing the header
        """

        headerstr = """
        INCLUDE "hardware.inc"
        SECTION "Header", ROM0[$100]

            jp PenguinEntry

            ds $150 - @, 0 ; Make room for the header

        """

        return headerstr

    def footer(self) -> str:
        """
        Generate the footer for the assembly code.
        
        Returns:
            A string containing the footer
        """
        footerstr = """
        PenguinDone:
        nop
        jp PenguinDone

        PenguinMult:
        ld a, 0
        ld d, 8
        .loop:
            srl b
            jp nc, .no_add 
            add a, c
        .no_add:
            sla c
            dec d
            jp nz, .loop
        ret

        PenguinMemCopy:
        ld a, [de]
        ld [hli], a
        inc de
        dec bc
        ld a, b
        or a, c
        jp nz, PenguinMemCopy
        ret

        Labelcontrol_LCDon:
        ld a, LCDCF_ON | LCDCF_BGON | LCDCF_OBJON
        ld [rLCDC], a
        ret
        
        Labelcontrol_LCDoff:
        ld a, 0
        ld [rLCDC], a
        ret
        
        Labelcontrol_waitVBlank:
        ld a, [rLY]
        cp 144
        jp c, Labelcontrol_waitVBlank    
        ret
        
        Labelcontrol_initDisplayRegs:
        ld a, %11100100
        ld [rBGP], a
        ld a, %11100100
        ld [rOBP0], a
        ret
        
        """

        return footerstr 

    def generate(self, instruction: IRInstruction) -> str:
        class_name = instruction.__class__.__name__
        generator_name = f"generate_{class_name[2:]}"  # Remove the 'IR' prefix
        
        if hasattr(self, generator_name):
            generator = getattr(self, generator_name)
            return generator(instruction)
        else:
            raise ValueError(f"No generator found for instruction type: {class_name}")

    def generate_BinaryOp(self,instruction: IRBinaryOp) -> str:
        # TODO: It is to complex
        
        returnstr = ""

        # +
        if instruction.op == '+':
            # if register a is already involved
            if instruction.left == 'a' or instruction.right == 'a':
                if instruction.left == 'a':
                    returnstr += f"add {instruction.left}, {instruction.right}\n"
                else:
                    returnstr += f"add {instruction.right}, {instruction.left}\n"
                    
            # Case when a is not involved
            else:
                returnstr += f"ld a, {instruction.left}\n"
                returnstr += f"add a, {instruction.right}\n"
            
            if instruction.dest != 'a':
                returnstr += f"ld {instruction.dest}, a\n"

            return returnstr

        # -
        elif instruction.op == '-':
            # if register a is already involved
            if instruction.left == 'a' or instruction.right == 'a':
                if instruction.left == 'a':
                    returnstr += f"dec {instruction.left}, {instruction.right}\n"
                else:
                    returnstr += ""
                    returnstr += f"dec {instruction.right}, {instruction.left}\n"

            # Case when a is not involved
            else:
                returnstr += f"ld a, {instruction.left}\n"
                returnstr += f"sub a, {instruction.right}\n"
            
            if instruction.dest != 'a':
                returnstr += f"ld {instruction.dest}, a\n"

            return returnstr

        # *
        elif instruction.op == '*':
            returnstr = "push bc\n"
            returnstr += "push de\n"
            returnstr += "push hl\n"
            returnstr += f"ld b, {instruction.left}\n"
            returnstr += f"ld c, {instruction.right}\n"
            returnstr += "call PenguinMult\n"
            returnstr += "pop hl\n"
            returnstr += "pop de\n"
            returnstr += "pop bc\n"
            returnstr += f"ld {instruction.dest}, a\n"
            return returnstr
            
        # ==
        elif instruction.op == '==':
            # If the left operand is already in the accumulator, we can skip loading and directly compare to the right.
            # Otherwise we load left into A first.
            true_lbl = f"EQ_TRUE_{self.cmp_counter}"
            end_lbl = f"EQ_END_{self.cmp_counter}"
            self.cmp_counter += 1

            # load left into accumulator if needed, then compare to right
            if instruction.left != 'a':
                returnstr += f"ld a, {instruction.left}\n"
                
            returnstr += f"cp {instruction.right}\n"

            # default false
            returnstr += f"ld {instruction.dest}, 0\n"
            
            # if zero flag set (A == right), jump to true
            returnstr += f"jp z, {true_lbl}\n"
            
            # else skip to end
            returnstr += f"jp {end_lbl}\n"

            # true branch: set dest = 1
            returnstr += f"{true_lbl}:\n"
            returnstr += f"ld {instruction.dest}, 1\n"
            
            # end label
            returnstr += f"{end_lbl}:\n"

            return returnstr
        
        # !=
        elif instruction.op == '!=':
            true_lbl = f"NE_TRUE_{self.cmp_counter}"
            end_lbl = f"NE_END_{self.cmp_counter}"
            self.cmp_counter += 1

            if instruction.left != 'a':
                returnstr += f"ld a, {instruction.left}\n"
                
            returnstr += f"cp {instruction.right}\n"
            returnstr += f"ld {instruction.dest}, 0\n"
            returnstr += f"jp nz, {true_lbl}\n"
            returnstr += f"jp {end_lbl}\n"
            returnstr += f"{true_lbl}:\n"
            returnstr += f"ld {instruction.dest}, 1\n"
            returnstr += f"{end_lbl}:\n"
            
            return returnstr
        # Bitwise and, &
        elif instruction.op == '&':
            # If A already holds one operand, AND the other; otherwise load left into A first
            if instruction.left == 'a':
                returnstr += f"and {instruction.right}\n"
            # If the right operand is already in the accumulator, AND the left
            elif instruction.right == 'a':
                returnstr += f"and {instruction.left}\n"
            else:
                # Neither operand is in A
                returnstr += f"ld a, {instruction.left}   ; load left into A\n"
                returnstr += f"and {instruction.right}\n"
            if instruction.dest != 'a':
                returnstr += f"ld {instruction.dest}, a   ; store\n"
            return returnstr

        # Logical AND 
            # A And B = Must be 0
        elif instruction.op == 'and':
            true_lbl = f"AND_TRUE_{self.cmp_counter}"
            end_lbl = f"AND_END_{self.cmp_counter}"
            self.cmp_counter += 1

            # assume false. If both are ≠ 0, then jump to true label
            returnstr += f"ld {instruction.dest}, 0    ; assume false\n"
            # if left == 0, end (false)
            if instruction.left != 'a':
                returnstr += f"ld a, {instruction.left}   ; load left\n"
            returnstr += "cp 0\n"
            returnstr += f"jp z, {end_lbl}\n"

            # if right == 0, end (false)
            returnstr += f"ld a, {instruction.right}   ; load right\n"
            returnstr += "cp 0\n"
            returnstr += f"jp z, {end_lbl}\n"

            # both ≠ 0 (true)
            returnstr += f"{true_lbl}:\n"
            returnstr += f"ld {instruction.dest}, 1   ; set true\n"
            returnstr += f"{end_lbl}:\n"
            return returnstr
        
        # Bitwise or, |
        elif instruction.op == '|':
            if instruction.left == 'a':
                returnstr += f"or {instruction.right}\n"
            # If the right operand is in A, OR the left
            elif instruction.right == 'a':
                returnstr += f"or {instruction.left}\n"
            else:
                # Neither operand in A, so load left first
                returnstr += f"ld a, {instruction.left}   ; load left into A\n"
                returnstr += f"or {instruction.right}\n"

            # Store the result if dest ≠ A
            if instruction.dest != 'a':
                returnstr += f"ld {instruction.dest}, a   ; store\n"
            return returnstr

        # Logical OR
            # A OR B Must not be 0
        elif instruction.op == 'or':
            # Assume true. If both operands == 0, then jump to false label
            true_lbl = f"OR_TRUE_{self.cmp_counter}"
            end_lbl = f"OR_END_{self.cmp_counter}"
            self.cmp_counter += 1

            # Check left ≠ 0
            if instruction.left != 'a':
                returnstr += f"ld a, {instruction.left}   ; load left\n"
            returnstr += "cp 0   ; compare left to 0\n"
            returnstr += f"jp nz, {true_lbl}   ; if nonzero, set true\n"

            # Check right ≠ 0
            returnstr += f"ld a, {instruction.right}   ; load right\n"
            returnstr += "cp 0   ; compare right to 0\n"
            returnstr += f"jp nz, {true_lbl}   ; if nonzero, set true\n"

            # False Case
            returnstr += f"ld {instruction.dest}, 0   ; set false\n"
            returnstr += f"jp {end_lbl}\n"

            # True case
            returnstr += f"{true_lbl}:\n"
            returnstr += f"ld {instruction.dest}, 1   ; set true\n"
            returnstr += f"{end_lbl}:\n"
            return returnstr
        
        # ^, xor
        elif instruction.op == '^':
            # If the left operand is already in the accumulator, we can skip loading and just 'xor' the right.
            if instruction.left == 'a':
                returnstr += f"xor {instruction.right}\n"
                
            # if the right operand is already in the accumulator, we can just 'xor' the left.
            elif instruction.right == 'a':
                returnstr += f"xor {instruction.left}\n"
            else:
                # None of the operands are in the accumulator, so we load left into the accumulator first.
                returnstr += f"ld a, {instruction.left}\n"
                returnstr += f"xor {instruction.right}\n"

            # After the 'xor' instruction, the result is in the accumulator.
            if instruction.dest != 'a':
                returnstr += f"ld {instruction.dest}, a\n"
                
            return returnstr
        
        # > greater than
        elif instruction.op == '>':
            # If the left operand is not already in the accumulator, load it into A.
            true_lbl = f"GT_TRUE_{self.cmp_counter}"
            end_lbl = f"GT_END_{self.cmp_counter}"
            self.cmp_counter += 1

            # Load left into the accumulator if needed, then compare to right
            if instruction.left != 'a':
                returnstr += f"ld a, {instruction.left}\n"
                
            returnstr += f"cp {instruction.right}\n"

            # Assume false: set dest = 0
            returnstr += f"ld {instruction.dest}, 0\n"
            
            # If carry flag set (A < right), skip the true branch
            returnstr += f"jp c, {end_lbl}\n"
            
            # If zero flag set (A == right), skip the true branch
            returnstr += f"jp z, {end_lbl}\n"

            # True branch: A > right
            returnstr += f"{true_lbl}:\n"
            returnstr += f"ld {instruction.dest}, 1\n"
            
            # End label
            returnstr += f"{end_lbl}:\n"
            
            return returnstr
        
        # < less than
        elif instruction.op == '<':
            # If the left operand is not already in the accumulator, load it into A.
            true_lbl = f"LT_TRUE_{self.cmp_counter}"
            end_lbl = f"LT_END_{self.cmp_counter}"
            self.cmp_counter += 1

            # Load left into the accumulator (A) if needed, then compare to right
            if instruction.left != 'a':
                returnstr += f"ld a, {instruction.left}\n"
                
            returnstr += f"cp {instruction.right}\n"

            # Assume false: set dest = 0
            returnstr += f"ld {instruction.dest}, 0\n"
            
            # If carry flag set (A < right), skip the true branch
            returnstr += f"jp c, {true_lbl}\n"
            
            # Otherwise skip over the true branch. 
            returnstr += f"jp {end_lbl}\n"

            # True branch: A < right, so dest = 1
            returnstr += f"{true_lbl}:\n"
            returnstr += f"ld {instruction.dest}, 1\n"
            
            # End label
            returnstr += f"{end_lbl}:\n"

            return returnstr
        
        # <= less than or equal
        elif instruction.op == '<=':
            # Generate unique labels for the true and end branches
            true_lbl = f"LE_TRUE_{self.cmp_counter}"
            end_lbl = f"LE_END_{self.cmp_counter}"
            self.cmp_counter += 1

            # Load left into A if needed, then compare to right
            if instruction.left != 'a':
                returnstr += f"ld a, {instruction.left}\n"
                
            returnstr += f"cp {instruction.right}\n"

            # Assume false: dest = 0
            returnstr += f"ld {instruction.dest}, 0\n"
            
            # If carry flag set (A < right), jump to true branch
            returnstr += f"jp c, {true_lbl}\n"
            
            # If zero flag set (A == right), also jump to true branch
            returnstr += f"jp z, {true_lbl}\n"
            
            # Otherwise skip over the true branch
            returnstr += f"jp {end_lbl}\n"

            # True branch: A <= right, so dest = 1
            returnstr += f"{true_lbl}:\n"
            
            returnstr += f"ld {instruction.dest}, 1\n"
            
            # End label
            returnstr += f"{end_lbl}:\n"

            return returnstr
        
        # >= greater than or equal to
        elif instruction.op == '>=':
            # Generate unique labels for the true and end branches
            true_lbl = f"GE_TRUE_{self.cmp_counter}"
            end_lbl = f"GE_END_{self.cmp_counter}"
            self.cmp_counter += 1

            # Load left into the accumulator if needed, then compare to right
            if instruction.left != 'a':
                returnstr += f"ld a, {instruction.left}\n"
                
            returnstr += f"cp {instruction.right}\n"

            # Assume false: set dest = 0
            returnstr += f"ld {instruction.dest}, 0\n"
            
            # If zero flag set (A == right), jump to true branch
            returnstr += f"jp z, {true_lbl}\n"
            
            # If carry flag is not set (A >= right), jump to true branch
            returnstr += f"jp nc, {true_lbl}\n"
            
            # Otherwise skip over the true branch
            returnstr += f"jp {end_lbl}\n"

            # True branch: A >= right, so dest = 1
            returnstr += f"{true_lbl}:\n"
            returnstr += f"ld {instruction.dest}, 1\n"
            
            # End label
            returnstr += f"{end_lbl}:\n"

            return returnstr
        
        # << shift left
        elif instruction.op == '<<':
            # Generate unique labels for our shift loop
            loop_lbl = f"SHL_LOOP_{self.cmp_counter}"
            end_lbl = f"SHL_END_{self.cmp_counter}"
            self.cmp_counter += 1

            # Load the value to shift into the accumulator (A) if needed
            if instruction.left != 'a':
                returnstr += f"ld a, {instruction.left}\n"
                
            # Load the shift count into B
            returnstr += f"ld b, {instruction.right}\n"

            # Loop: When shifting left, all newly-inserted bits are reset. Shifted on to A, then decrement B, repeat while B ≠ 0
            returnstr += f"{loop_lbl}:\n"
            returnstr += "sla a       ; shift A left by 1 bit\n"
            returnstr += "dec b       ; decrement loop counter\n"
            returnstr += f"jp nz, {loop_lbl}   ; repeat until B == 0\n"

            # After shifting, result is in A. Store it if dest ≠ A
            if instruction.dest != 'a':
                returnstr += f"ld {instruction.dest}, a\n"
                
            return returnstr
        
        # >> shift right (sign extension)
        elif instruction.op == '>>':
            # Generate unique labels for our shift loop
            loop_lbl = f"SHR_LOOP_{self.cmp_counter}"
            end_lbl = f"SHR_END_{self.cmp_counter}"
            self.cmp_counter += 1

            # Load the value to shift into the accumulator (A) if needed
            if instruction.left != 'a':
                returnstr += f"ld a, {instruction.left}\n"
                
            # Load the shift count into B
            returnstr += f"ld b, {instruction.right}\n"

            # Loop: when shifting right, they are copies of the original most significant bit instead. repeat while B ≠ 0
            returnstr += f"{loop_lbl}:\n"
            returnstr += "srl a       ; shift A right by (logical)\n"
            returnstr += "dec b\n"
            returnstr += f"jp nz, {loop_lbl}   ; repeat until B == 0\n"

            # After shifting, result is in A. Store it if dest ≠ A
            if instruction.dest != 'a':
                returnstr += f"ld {instruction.dest}, a\n"
                
            return returnstr

    def generate_UnaryOp(self,instruction: IRUnaryOp) -> str:
        returnstr = ""

        # ~
        if instruction.op == '~':
            returnstr += 'temp\n'

        # not
        elif instruction.op == 'not':
            returnstr += 'temp\n'

        return returnstr  

    def generate_IncBin(self,instruction: IRIncBin) -> str:
        returnstr = ""

        returnstr += f"Label{instruction.varname}Start:\n"
        returnstr += f"INCBIN {instruction.filepath}\n"
        returnstr += f"Label{instruction.varname}End:\n"

        self.include_binaries.append(returnstr)
        return "; include binary hooked to below footer\n"

    def generate_Assign(self,instruction: IRAssign) -> str:
        returnstr = ""
        if instruction.dest != instruction.src:
            returnstr += f"ld {instruction.dest}, {instruction.src}\n"
            
        return returnstr

    def generate_Constant(self,instruction: IRConstant) -> str:
        returnstr = f"ld {instruction.dest}, {instruction.value}\n"
        
        return returnstr

    def generate_Load(self,instruction: IRLoad) -> str:
        returnstr = ""
        
        if instruction.addr in self.variable_address_dict:
            returnstr += f"ld hl, {self.variable_address_dict[instruction.addr]}\n"
        else:
            returnstr += f"ld hl, {instruction.addr[1:-1]}\n"
            
        returnstr += "ld a, [hl]\n"
        
        if instruction.dest != 'a':
            returnstr += f"ld {instruction.dest}, a\n"
            
        return returnstr

    def generate_Store(self,instruction: IRStore) -> str:
        returnstr = ""
        
        if instruction.value != 'a':
            returnstr += f"ld a, {instruction.value}\n"
            
        # Case of normal variable
        if instruction.addr in self.variable_address_dict:
            
            returnstr += f"ld hl, {self.variable_address_dict[instruction.addr]}\n"
        # Case of spill and stack pointer
        else:
            returnstr += f"ld hl, {instruction.addr[1:-1]}\n"
            
        returnstr += "ld [hl], a\n"
        
        return returnstr

    def generate_Label(self,instruction: IRLabel) -> str:
        # TODO: Implementation to be filled in
        returnstr = f"{instruction.name}:\n"
        
        return returnstr

    def generate_Jump(self,instruction: IRJump) -> str:
        # TODO: Implementation to be filled in
        returnstr = f"jp {instruction.label}\n"
        
        return returnstr

    def generate_CondJump(self,instruction: IRCondJump) -> str:
        returnstr = ""
        
        if instruction.condition != 'a':
            returnstr += f"ld a, {instruction.condition}\n"
            
        returnstr += "cp 0\n"
        returnstr += f"jp nz, {instruction.true_label}\n"
        
        if instruction.false_label:
            returnstr += f"jp {instruction.false_label}\n"

        return returnstr

    def generate_Call(self,instruction: IRCall) -> str:
        listofregs = ['b', 'c', 'd', 'e']
        lines = []

        # Push registers onto stack
        lines.append("push bc")
        lines.append("push de")
        lines.append("push hl")

        # Place variables on the stack
        for param in instruction.args:
            lines.append("dec sp")
            lines.append("ld hl, sp + 0")
            lines.append(f"ld [hl], {param}")

        # Load arguments from stack into registers
        for i in range(len(instruction.args) - 1, -1, -1):
            lines.append("ld hl, sp + 0")
            lines.append(f"ld {listofregs[i]}, [hl]")
            lines.append("add sp, 1")

        # Call the procedure
        lines.append(f"call Label{instruction.proc_name}")

        # Result is in A
        lines.append("pop hl")
        lines.append("pop de")
        lines.append("pop bc")

        # Store result in destination register if specified
        if instruction.dest:
            lines.append(f"ld {instruction.dest}, a")

        lines.append("\n")

        returnstr = "\n".join(lines)
            
        return returnstr

    def generate_Return(self,instruction: IRReturn) -> str:
        lines = []
        if instruction.value and instruction.value != 'a':
            lines.append(f"ld a, {instruction.value}")
            
        lines.append("ret")
        lines.append("\n")

        returnstr = "\n".join(lines)
        return returnstr

    def generate_IndexedLoad(self,instruction: IRIndexedLoad) -> str:
        # TODO: Implementation to be filled in
        returnstr = ""
        
        return returnstr

    def generate_IndexedStore(self, instruction: IRIndexedStore) -> str:
        # TODO: Implementation to be filled in
        returnstr = ""
        
        return returnstr

    def generate_HardwareLoad(self, instruction: IRHardwareLoad) -> str:
        lines = [
            f"ld hl, {self.registerDict[instruction.register]}",
            "ld a, [hl]"
        ]
        
        if instruction.dest != 'a':
            lines.append(f"ld {instruction.dest}, a")

        returnstr = "\n".join(lines)
            
        return returnstr

    def generate_HardwareStore(self, instruction: IRHardwareStore) -> str:
        lines = [
            f"ld a, {instruction.value}",
            f"ld hl, {self.registerDict[instruction.register]}",
            "ld [hl], a",
        ]
        
        returnstr = "\n".join(lines)
    
        return returnstr

    def generate_HardwareIndexedLoad(self, instruction: IRHardwareIndexedLoad) -> str:
        lines = [
            f"ld a, {instruction.index}",
            "push bc",
            "push de",
            "push hl",
            f"ld hl, {self.registerDict[instruction.register]}",
        ]

        # Conditional load size
        lines.append("ld bc, 4" if "display_oam" in instruction.register else "ld bc, 1")

        # Loop code
        lines += [
            f"HwLoadLoop{self.cmp_counter}:",
            "cp 0",
            f"jp z, HwLoadLoopDone{self.cmp_counter}",
            "add hl, bc",
            "dec a",
            f"jp HwLoadLoop{self.cmp_counter}",
            f"HwLoadLoopDone{self.cmp_counter}:",
            "ld a, [hl]",
            "pop hl",
            "pop de",
            "pop bc",
        ]

        # Optional register transfer
        if instruction.dest != 'a':
            lines.append(f"ld {instruction.dest}, a")

        self.cmp_counter += 1
        
        returnstr = "\n".join(lines)
            
        return returnstr

    def generate_HardwareIndexedStore(self, instruction: IRHardwareIndexedStore) -> str:
        lines = [
            f"ld a, {instruction.index}",
            f"ld d, {instruction.value}",
            "push bc",
            "push de",
            "push hl",
            f"ld hl, {self.registerDict[instruction.register]}",
        ]

        # Conditionally add the `ld bc` line
        if "display_oam" in instruction.register:
            lines.append("ld bc, 4")
        else:
            lines.append("ld bc, 1")

        lines += [
            f"HwStoreLoop{self.cmp_counter}:",
            "cp 0",
            f"jp z, HwStoreLoopDone{self.cmp_counter}",
            "add hl, bc",
            "dec a",
            f"jp HwStoreLoop{self.cmp_counter}",
            f"HwStoreLoopDone{self.cmp_counter}:",
            "ld a, d",
            "ld [hl], a",
            "pop hl",
            "pop de",
            "pop bc",
        ]

        self.cmp_counter += 1

        lines.append("\n")

        returnstr = "\n".join(lines)
        
        return returnstr

    def generate_HardwareMemCpy(self,instruction: IRHardwareMemCpy) -> str:
        lines = [
            "push bc",
            "push de",
            "push hl",
            f"ld de, Label{instruction.src}Start",
            f"ld hl, {self.registerDict[instruction.dest]}",
            f"ld bc, Label{instruction.src}End - Label{instruction.src}Start",
            "call PenguinMemCopy",
            "pop hl",
            "pop de",
            "pop bc"
        ]
        
        returnstr = "\n".join(lines)

        return returnstr

    def generate_ArgLoad(self,instruction: IRArgLoad) -> str:
        # Implementation to be filled in
        returnstr = "; Arg was loaded\n"
        
        return returnstr 
    
    def generate_ChangeSP(self, instruction: IRChangeSP) -> str:
        returnstr = ""
        if instruction.op == '+':
            returnstr += f"add sp, {instruction.amount}\n"
        else:
            returnstr += f"add sp, -{instruction.amount}\n"
            
        return returnstr
