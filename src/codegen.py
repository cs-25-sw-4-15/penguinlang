import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.IRProgram import *
from src.codegenRegisters import *
from src.logger import logger


class CodeGenerator:

    def __init__(self):
        
        self.variable_address_dict = {}
        self.cmp_counter = 0
        self.registerDict = codegenRegister()
        self.include_binaries = []

    def generate_code(self, ir_program: IRProgram) -> str:
        
        self.variable_address_dict = ir_program.global_address
        assembly_code = ""
        
        assembly_code += self.header()

        assembly_code += "PenguinEntry:\n"
        assembly_code += "ld sp, $DFFF\n"
        assembly_code += "ld a, 0\n"
        assembly_code += "ld [wCurKeys], a\n"
        assembly_code += "ld [wNewKeys], a\n"

        for instruction in ir_program.main_instructions:
            assembly_line = self.generate(instruction)
            
            if assembly_line:
                assembly_code += assembly_line + "\n"

        for procedure in ir_program.procedures.items():
            if procedure[0] not in self.footer():
                assembly_code += f"Label{procedure[0]}:\n"
            
            for instruction in procedure[1].instructions:
                assembly_line = self.generate(instruction)
                
                if assembly_line:
                    assembly_code += assembly_line
            
        assembly_code += self.footer()
        total_binaries = "\n".join(self.include_binaries)
        assembly_code += total_binaries

        assembly_code += "\n"
        assembly_code += "SECTION \"Input Variables\", WRAM0\n"
        assembly_code += "wCurKeys: db\n"
        assembly_code += "wNewKeys: db\n"

        formatted_lines = []
        for line in assembly_code.splitlines():
            stripped_line = line.strip()
            if stripped_line:
                if stripped_line.endswith(":"):
                    formatted_lines.append(stripped_line)
                else:
                    formatted_lines.append("  " + stripped_line)
        return "\n".join(formatted_lines)

    def header(self) -> str:

        headerstr = """
        INCLUDE "hardware.inc"
        SECTION "Header", ROM0[$100]
            jp PenguinEntry

            ds $150 - @, 0 ; Make room for the header

        """

        return headerstr

    def footer(self) -> str:
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
        
        Labelcontrol_waitVBlankStart:
        ld a, [rLY]
        cp 144
        jp c, Labelcontrol_waitVBlankStart
        ret
        
        Labelcontrol_waitVBlankOver:
        ld a, [rLY]
        cp 144
        jp nc, Labelcontrol_waitVBlankOver
        ret
        
        Labelcontrol_initPalette:
        ld a, 0b11100100
        ld [rBGP], a
        ld [$FF48], a
        ld [$FF49], a
        ret
        
        Labelcontrol_initDisplayRegs:
        ld a, %11100100
        ld [rBGP], a
        ld a, %11100100
        ld [rOBP0], a
        ret
        
        Labelcontrol_updateInput:
        ld a, P1F_GET_BTN
        call .onenibble
        ld b, a
        
        ld a, P1F_GET_DPAD
        call .onenibble
        swap a
        xor a, b
        ld b, a
        ld a, P1F_GET_NONE
        ldh [rP1], a
        ld a, [wCurKeys]
        xor a, b
        and a, b
        ld [wNewKeys], a
        ld a, b
        ld [wCurKeys], a
        ret

        .onenibble
        ldh [rP1], a
        call .knownret
        ldh a, [rP1]
        ldh a, [rP1]
        ldh a, [rP1]
        or a, $F0
        .knownret
        ret
        
        Labelcontrol_checkLeft:
            ld a, [wCurKeys]
            and a, PADF_LEFT
            ret
            
        Labelcontrol_checkRight:
            ld a, [wCurKeys]
            and a, PADF_RIGHT
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
            true_lbl = f"EQ_TRUE_{self.cmp_counter}"
            end_lbl = f"EQ_END_{self.cmp_counter}"
            self.cmp_counter += 1

            if instruction.left != 'a':
                returnstr += f"ld a, {instruction.left}\n"
                
            returnstr += f"cp {instruction.right}\n"

            returnstr += f"ld {instruction.dest}, 0\n"
            
            returnstr += f"jp z, {true_lbl}\n"
            
            returnstr += f"jp {end_lbl}\n"

            returnstr += f"{true_lbl}:\n"
            returnstr += f"ld {instruction.dest}, 1\n"
            
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
        
        elif instruction.op == '&':
            if instruction.left == 'a':
                returnstr += f"and {instruction.right}\n"
            elif instruction.right == 'a':
                returnstr += f"and {instruction.left}\n"
            else:
                returnstr += f"ld a, {instruction.left}   ; load left into A\n"
                returnstr += f"and {instruction.right}\n"
            if instruction.dest != 'a':
                returnstr += f"ld {instruction.dest}, a   ; store\n"
            return returnstr

        # Logical AND 
        elif instruction.op == 'and':
            true_lbl = f"AND_TRUE_{self.cmp_counter}"
            end_lbl = f"AND_END_{self.cmp_counter}"
            self.cmp_counter += 1

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
            elif instruction.right == 'a':
                returnstr += f"or {instruction.left}\n"
            else:
                returnstr += f"ld a, {instruction.left}   ; load left into A\n"
                returnstr += f"or {instruction.right}\n"

            if instruction.dest != 'a':
                returnstr += f"ld {instruction.dest}, a   ; store\n"
            return returnstr

        # Logical OR
        elif instruction.op == 'or':
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
            if instruction.left == 'a':
                returnstr += f"xor {instruction.right}\n"
                
            elif instruction.right == 'a':
                returnstr += f"xor {instruction.left}\n"
            else:
                returnstr += f"ld a, {instruction.left}\n"
                returnstr += f"xor {instruction.right}\n"

            if instruction.dest != 'a':
                returnstr += f"ld {instruction.dest}, a\n"
                
            return returnstr
        
        # > greater than
        elif instruction.op == '>':
            true_lbl = f"GT_TRUE_{self.cmp_counter}"
            end_lbl = f"GT_END_{self.cmp_counter}"
            self.cmp_counter += 1

            if instruction.left != 'a':
                returnstr += f"ld a, {instruction.left}\n"
                
            returnstr += f"cp {instruction.right}\n"

            returnstr += f"ld {instruction.dest}, 0\n"
            
            returnstr += f"jp c, {end_lbl}\n"
            
            returnstr += f"jp z, {end_lbl}\n"

            returnstr += f"{true_lbl}:\n"
            returnstr += f"ld {instruction.dest}, 1\n"
            
            returnstr += f"{end_lbl}:\n"
            
            return returnstr
        
        # < less than
        elif instruction.op == '<':
            true_lbl = f"LT_TRUE_{self.cmp_counter}"
            end_lbl = f"LT_END_{self.cmp_counter}"
            self.cmp_counter += 1

            if instruction.left != 'a':
                returnstr += f"ld a, {instruction.left}\n"
                
            returnstr += f"cp {instruction.right}\n"

            returnstr += f"ld {instruction.dest}, 0\n"
            
            returnstr += f"jp c, {true_lbl}\n"
            
            returnstr += f"jp {end_lbl}\n"

            returnstr += f"{true_lbl}:\n"
            returnstr += f"ld {instruction.dest}, 1\n"
            
            returnstr += f"{end_lbl}:\n"

            return returnstr
        
        # <= less than or equal
        elif instruction.op == '<=':
            true_lbl = f"LE_TRUE_{self.cmp_counter}"
            end_lbl = f"LE_END_{self.cmp_counter}"
            self.cmp_counter += 1

            if instruction.left != 'a':
                returnstr += f"ld a, {instruction.left}\n"
                
            returnstr += f"cp {instruction.right}\n"

            returnstr += f"ld {instruction.dest}, 0\n"
            
            returnstr += f"jp c, {true_lbl}\n"
            
            returnstr += f"jp z, {true_lbl}\n"
            
            returnstr += f"jp {end_lbl}\n"

            returnstr += f"{true_lbl}:\n"
            
            returnstr += f"ld {instruction.dest}, 1\n"
            
            returnstr += f"{end_lbl}:\n"

            return returnstr
        
        # >= greater than or equal to
        elif instruction.op == '>=':
            true_lbl = f"GE_TRUE_{self.cmp_counter}"
            end_lbl = f"GE_END_{self.cmp_counter}"
            self.cmp_counter += 1

            if instruction.left != 'a':
                returnstr += f"ld a, {instruction.left}\n"
                
            returnstr += f"cp {instruction.right}\n"

            returnstr += f"ld {instruction.dest}, 0\n"
            
            returnstr += f"jp z, {true_lbl}\n"
            
            returnstr += f"jp nc, {true_lbl}\n"
            
            returnstr += f"jp {end_lbl}\n"

            returnstr += f"{true_lbl}:\n"
            returnstr += f"ld {instruction.dest}, 1\n"
            
            returnstr += f"{end_lbl}:\n"

            return returnstr
        
        # << shift left
        elif instruction.op == '<<':
            loop_lbl = f"SHL_LOOP_{self.cmp_counter}"
            end_lbl = f"SHL_END_{self.cmp_counter}"
            self.cmp_counter += 1

            if instruction.left != 'a':
                returnstr += f"ld a, {instruction.left}\n"
                
            returnstr += f"ld b, {instruction.right}\n"

            returnstr += f"{loop_lbl}:\n"
            returnstr += "sla a       ; shift A left by 1 bit\n"
            returnstr += "dec b       ; decrement loop counter\n"
            returnstr += f"jp nz, {loop_lbl}   ; repeat until B == 0\n"

            if instruction.dest != 'a':
                returnstr += f"ld {instruction.dest}, a\n"
                
            return returnstr
        
        # >> shift right (sign extension)
        elif instruction.op == '>>':

            loop_lbl = f"SHR_LOOP_{self.cmp_counter}"
            end_lbl = f"SHR_END_{self.cmp_counter}"
            self.cmp_counter += 1
            returnstr += f"; shift right begin\n"
            if instruction.left != 'a':
                returnstr += f"ld a, {instruction.left}\n"

            returnstr += "push bc\n"
                
            returnstr += f"ld b, {instruction.right}\n"

            returnstr += f"{loop_lbl}:\n"
            returnstr += "srl a       ; shift A right by (logical)\n"
            returnstr += "dec b\n"
            returnstr += f"jp nz, {loop_lbl}   ; repeat until B == 0\n"

            returnstr += "pop bc\n"

            if instruction.dest != 'a':
                returnstr += f"ld {instruction.dest}, a\n"

            returnstr += f"; shift right end\n"

                
            return returnstr

    def generate_UnaryOp(self,instruction: IRUnaryOp) -> str:
        returnstr = ""

        # ~
        if instruction.op == '~':
            returnstr += ';Not implemented\n'

        # not
        elif instruction.op == 'not':
            returnstr += ';Not implemented\n'

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

        for param in instruction.args:
            lines.append("dec sp")
            lines.append("ld hl, sp + 0")
            lines.append(f"ld [hl], {param}")

        # Load arguments from stack into registers
        for i in range(len(instruction.args) - 1, -1, -1):
            lines.append("ld hl, sp + 0")
            lines.append(f"ld {listofregs[i]}, [hl]")
            lines.append("add sp, 1")

        lines.append(f"call Label{instruction.proc_name}")

        lines.append("pop hl")
        lines.append("pop de")
        lines.append("pop bc")

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
        if "display_oam" in instruction.register:
            skip = 4
        else:
            skip = 1

        self.cmp_counter += 2

        lines = [
            "push bc",
            "push de",
            "push hl",
            f"ld e, {skip}",
            f"ld c, {instruction.index}",
            "ld b, 0",
            "ld d, 8",
            "ld hl, 0",
            f"loop{self.cmp_counter-1}:",
            "srl e",
            f"jp nc, no_add{self.cmp_counter-2}",
            "add hl, bc",
            f"no_add{self.cmp_counter-2}:",
            "sla c",
            "rl b",
            "dec d",
            f"jp nz, loop{self.cmp_counter-1}",
            f"ld bc, {self.registerDict[instruction.register]}", # offset in hl, base in bc
            f"add hl, bc",
            "pop bc",
            f"ld {instruction.dest}, [hl]",
            "pop hl",
            "pop de\n",
        ]

        return "\n".join(lines)

    def generate_HardwareIndexedStore(self, instruction: IRHardwareIndexedStore) -> str:
        if "display_oam" in instruction.register:
            skip = 4
        else:
            skip = 1

        self.cmp_counter += 2

        lines = [
            "push bc",
            "push de",
            "push hl",
            f"ld a, {instruction.value}",
            f"ld e, {skip}",
            f"ld c, {instruction.index}",
            "ld b, 0",
            "ld d, 8",
            "ld hl, 0",
            f"loop{self.cmp_counter-1}:",
            "srl e",
            f"jp nc, no_add{self.cmp_counter-2}",
            "add hl, bc",
            f"no_add{self.cmp_counter-2}:",
            "sla c",
            "rl b",
            "dec d",
            f"jp nz, loop{self.cmp_counter-1}",
            f"ld bc, {self.registerDict[instruction.register]}", # offset in hl, base in bc
            f"add hl, bc",
            f"ld [hl], a",
            "pop hl",
            "pop de",
            "pop bc\n",
        ]

        return "\n".join(lines)

    def generate_HardwareIndexedDoubleLoad(self, instruction: IRHardwareIndexedDoubleLoad) -> str:
        self.cmp_counter += 2

        lines = [
            "push hl",
            "push de",
            "push bc",
            f"ld l, {instruction.index}",
            f"ld e, 32",
            f"ld c, {instruction.index2}",
            "ld b, 0",
            "ld d, 8",
            "ld h, 0",
            f"loop{self.cmp_counter-1}:",
            "srl e",
            f"jp nc, no_add{self.cmp_counter-2}",
            "add hl, bc",
            f"no_add{self.cmp_counter-2}:",
            "sla c",
            "rl b",
            "dec d",
            f"jp nz, loop{self.cmp_counter-1}",
            f"ld bc, {self.registerDict[instruction.register]}", # offset in hl, base in bc
            f"add hl, bc",
            "pop bc",
            "pop de",
            f"ld {instruction.dest}, [hl]",
            "pop hl\n"
        ]

        return "\n".join(lines)

    def generate_HardwareIndexedDoubleStore(self, instruction: IRHardwareIndexedDoubleStore) -> str:
        self.cmp_counter += 2

        lines = [
            "push bc",
            "push de",
            "push hl",
            f"ld a, {instruction.value}",
            f"ld l, {instruction.index}",
            f"ld e, 32",
            f"ld c, {instruction.index2}",
            "ld b, 0",
            "ld d, 8",
            "ld h, 0",
            f"loop{self.cmp_counter-1}:",
            "srl e",
            f"jp nc, no_add{self.cmp_counter-2}",
            "add hl, bc",
            f"no_add{self.cmp_counter-2}:",
            "sla c",
            "rl b",
            "dec d",
            f"jp nz, loop{self.cmp_counter-1}",
            f"ld bc, {self.registerDict[instruction.register]}", # offset in hl, base in bc
            f"add hl, bc",
            f"ld [hl], a",
            "pop hl",
            "pop de",
            "pop bc\n"
        ]

        return "\n".join(lines)

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
