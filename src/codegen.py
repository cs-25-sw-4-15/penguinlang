from IRProgram import *

class CodeGenerator:

    def __init__(self):
        """
        Initialize the code generator.
        """
        self.variable_address_dict = {}
        pass

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
            #add label for procedure
            assembly_code += f"Label{procedure[0]}:\n"
            for instruction in procedure[1].instructions:
                assembly_line = self.generate(instruction)
                if assembly_line:
                    assembly_code += assembly_line
            

        assembly_code += self.footer()
        
        return assembly_code

    def header(self) -> str:
        """
        Generate the header for the assembly code.
        
        Returns:
            A string containing the header
        """

        headerstr = """
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
        PenguinPush:
        push bc
        push de
        push hl
        ret

        PenguinPop:
        pop bc
        pop de
        pop hl
        ret

        PenguinMult:
        ;not implemented

        PenguinCalcOffset:

        PenguinMemCopy:
        ld a, [de]
        ld [hli], a
        inc de
        dec bc
        ld a, b
        or a, c
        jp nz, PenguinMemCopy
        ret


        control_LCDon:
        ld a, $91
        ld [$FF40], a
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
        # Implementation to be filled in
        returnstr = ""

        # +
        if instruction.op == '+':
            #if register a is already involved
            if instruction.left == 'a' or instruction.right == 'a':
                if instruction.left == 'a':
                    returnstr += f"add {instruction.left}, {instruction.right}\n"
                else:
                    returnstr += f"add {instruction.right}, {instruction.left}\n"
            #Case when a is not involved
            else:
                returnstr += f"ld a, {instruction.left}\n"
                returnstr += f"add a, {instruction.right}\n"
            
            if instruction.dest != 'a':
                returnstr += f"ld {instruction.dest}, a\n"

            return returnstr

        # -
        elif instruction.op == '-':
            #if register a is already involved
            if instruction.left == 'a' or instruction.right == 'a':
                if instruction.left == 'a':
                    returnstr += f"dec {instruction.left}, {instruction.right}\n"
                else:
                    returnstr += f""
                    returnstr += f"dec {instruction.right}, {instruction.left}\n"

            #Case when a is not involved
            else:
                returnstr += f"ld a, {instruction.left}\n"
                returnstr += f"sub a, {instruction.right}\n"
            
            if instruction.dest != 'a':
                returnstr += f"ld {instruction.dest}, a\n"

            return returnstr

        # *
        elif instruction.op == '*':
            """GB DOES NOT HAVE MULTIPLY, USE HELPER FUNCTION IN FOOTER"""
            #PUSH REGISTERS
            #LOAD PARAMS
            #CALL MULTIPLY
            #POP REGISTERS
            #STORE RESULT
            returnstr += f"TEMP MULTIPLY\n"



        # ==
        # !=
        # <
        # >
        # <=
        # >=
        # and
        # or
        # ^
        # & 
        # |
        # <<
        # >>
        
            
        

    def generate_UnaryOp(self,instruction: IRUnaryOp) -> str:
        # Implementation to be filled in
        returnstr = ""

        #~
        if instruction.op == '~':
            returnstr += 'temp\n'

        #not
        elif instruction.op == 'not':
            returnstr += 'temp\n'

        return returnstr
        

    def generate_IncBin(self,instruction: IRIncBin) -> str:
        # Implementation to be filled in
        returnstr = ""

        returnstr += f"Label{instruction.varname}Start:\n"
        returnstr += f"INCBIN {instruction.filepath}\n"
        returnstr += f"Label{instruction.varname}End:\n"

        return returnstr



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
        returnstr += f"ld a, [hl]\n"
        if instruction.dest != 'a':
            returnstr += f"ld {instruction.dest}, a\n"
        return returnstr

    def generate_Store(self,instruction: IRStore) -> str:
        returnstr = ""
        if instruction.value != 'a':
            returnstr += f"ld a, {instruction.value}\n"
        #Case of normal variable
        if instruction.addr in self.variable_address_dict:
            returnstr += f"ld hl, {self.variable_address_dict[instruction.addr]}\n"
        #Case of spill and stack pointer
        else:
            returnstr += f"ld hl, {instruction.addr[1:-1]}\n"
        returnstr += f"ld [hl], a\n"
        return returnstr


    def generate_Label(self,instruction: IRLabel) -> str:
        # Implementation to be filled in
        returnstr = f"{instruction.name}:\n"
        return returnstr

    def generate_Jump(self,instruction: IRJump) -> str:
        # Implementation to be filled in
        returnstr = f"jp {instruction.label}\n"
        return returnstr

    def generate_CondJump(self,instruction: IRCondJump) -> str:
        returnstr = ""
        if instruction.condition != 'a':
            returnstr += f"ld a, {instruction.condition}\n"
        returnstr += f"cp 0\n"
        returnstr += f"jp nz, {instruction.true_label}\n"
        if instruction.false_label:
            returnstr += f"jp {instruction.false_label}\n"

        return returnstr

    def generate_Call(self,instruction: IRCall) -> str:
        # Implementation to be filled in
        returnstr = ""
        #returnstr += f"call PenguinPush\n"
        returnstr += "push bc\n"
        returnstr += "push de\n"
        returnstr += "push hl\n"
        returnstr += f"call Label{instruction.proc_name}\n"
        #Placer variables
        #Call den reele funktion
        #Result er i A
        #returnstr += f"call PenguinPop\n"
        returnstr += "pop hl\n"
        returnstr += "pop de\n"
        returnstr += "pop bc\n"
        return returnstr

    def generate_Return(self,instruction: IRReturn) -> str:
        # Implementation to be filled in
        returnstr = ""
        if instruction.value and instruction.value != 'a':
            returnstr += f"ld a, {instruction.value}\n"
        returnstr += "ret\n"
        return returnstr

    def generate_IndexedLoad(self,instruction: IRIndexedLoad) -> str:
        # Implementation to be filled in
        returnstr = ""

    def generate_IndexedStore(self, instruction: IRIndexedStore) -> str:
        # Implementation to be filled in
        returnstr = ""

    def generate_HardwareLoad(self, instruction: IRHardwareLoad) -> str:
        # Implementation to be filled in
        returnstr = ""
        returnstr += f"ld a, [{instruction.register}]\n"
        if instruction.dest != 'a':
            returnstr += f"ld {instruction.dest}, a\n"
        return returnstr

    def generate_HardwareStore(self, instruction: IRHardwareStore) -> str:
        # Implementation to be filled in
        returnstr = ""
        returnstr += f"ld a, {instruction.value}\n"
        returnstr += f"ld [{instruction.register}], a\n"
        return returnstr

    def generate_HardwareIndexedLoad(self, instruction: IRHardwareIndexedLoad) -> str:
        # Implementation to be filled in
        returnstr = ""

    def generate_HardwareIndexedStore(self, instruction: IRHardwareIndexedStore) -> str:
        # Implementation to be filled in
        returnstr = ""

    def generate_HardwareMemCpy(self,instruction: IRHardwareMemCpy) -> str:
        # Implementation to be filled in
        returnstr = ""
        returnstr += f"call PenguinPush\n"
        returnstr += f"ld de, Label{instruction.src}Start\n"
        returnstr += f"ld hl, {instruction.dest}\n"
        returnstr += f"ld bc, Label{instruction.src}End - {instruction.src}Start\n"
        returnstr += f"call PenguinMemCopy\n"
        returnstr += f"call PenguinPop\n"
        returnstr += f""
        return returnstr

    def generate_ArgLoad(self,instruction: IRArgLoad) -> str:
        # Implementation to be filled in
        returnstr = ""
        return "; Arg was loaded\n"   
    
    def generate_ChangeSP(self, instruction: IRChangeSP) -> str:
        returnstr = ""
        if instruction.op == '+':
            returnstr += f"add sp, {instruction.amount}\n"
        else:
            returnstr += f"add sp, -{instruction.amount}\n"
        return returnstr
