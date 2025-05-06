from IRProgram import *

class CodeGenerator:

    def __init__(self):
        """
        Initialize the code generator.
        """
        pass

    def generate_code(self, ir_program: IRProgram) -> str:
        """
        Generate assembly code from an IR program.
        
        Args:
            ir_program: The IR program to generate code for
            
        Returns:
            A string containing the generated assembly code
        """
        # Initialize the assembly code string
        assembly_code = ""
        
        assembly_code += self.header()

        # Iterate over each instruction in the IR program
        for instruction in ir_program.instructions:
            # Convert the instruction to assembly code
            assembly_line = self.generate(instruction)
            # Append the assembly line to the code string
            assembly_code += assembly_line + "\n"

        assembly_code += self.footer()
        
        return assembly_code

    def header() -> str:
        """
        Generate the header for the assembly code.
        
        Returns:
            A string containing the header
        """
        return "header"


    def footer() -> str:
        """
        Generate the footer for the assembly code.
        
        Returns:
            A string containing the footer
        """
        return "footer" 

    def generate(instruction: IRInstruction) -> str:
        """Generate code for the given IR instruction by dispatching to the appropriate generator"""
        class_name = instruction.__class__.__name__
        generator_name = f"generate_{class_name[2:]}"  # Remove the 'IR' prefix
        generator = globals().get(generator_name)
        
        if generator is None:
            raise ValueError(f"No generator found for instruction type: {class_name}")
        
        return generator(instruction)

    def generate_BinaryOp(instruction: IRBinaryOp) -> str:
        # Implementation to be filled in
        returnstr = ""

        # +
        if instruction.op == '+':
            #if register a is already involved
            if instruction.src1 == 'a' or instruction.src2 == 'a':
                if instruction.src1 == 'a':
                    returnstr += f"add {instruction.src1}, {instruction.src2}\n"
                else:
                    returnstr += f"add {instruction.src2}, {instruction.src1}\n"
            #Case when a is not involved
            else:
                returnstr += f"ld a, {instruction.src1}\n"
                returnstr += f"add a, {instruction.src2}\n"
            
            if instruction.dest != 'a':
                returnstr += f"ld {instruction.dest}, a\n"

            return returnstr

        # -
        elif instruction.op == '-':
            #if register a is already involved
            if instruction.src1 == 'a' or instruction.src2 == 'a':
                if instruction.src1 == 'a':
                    returnstr += f"dec {instruction.src1}, {instruction.src2}\n"
                else:
                    returnstr += f"dec {instruction.src2}, {instruction.src1}\n"

            #Case when a is not involved
            else:
                returnstr += f"ld a, {instruction.src1}\n"
                returnstr += f"dec a, {instruction.src2}\n"
            
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
        
            
        

    def generate_UnaryOp(instruction: IRUnaryOp) -> str:
        # Implementation to be filled in
        returnstr = ""

        #~
        #not

    def generate_IncBin(instruction: IRIncBin) -> str:
        # Implementation to be filled in
        returnstr = ""

        returnstr += f"Label{instruction.varname}Start\n"
        returnstr += f"INCBIN {instruction.filepath}\n"
        returnstr += f"Label{instruction.varname}End\n"

        return returnstr



    def generate_Assign(instruction: IRAssign) -> str:
        # Implementation to be filled in
        returnstr = ""
        returnstr += f"ld {instruction.dest}, {instruction.src}\n"
        return returnstr

    def generate_Constant(instruction: IRConstant) -> str:
        # Implementation to be filled in
        returnstr = f"ld {instruction.dest}, {instruction.value}"
        return returnstr

    def generate_Load(instruction: IRLoad) -> str:
        # Implementation to be filled in
        returnstr = ""
        returnstr += f"ld hl, {instruction.addr}\n"
        returnstr += f"ld a, [hl]\n"
        returnstr += f"ld {instruction.dest}, a\n"
        return returnstr

    def generate_Store(instruction: IRStore) -> str:
        # Implementation to be filled in
        returnstr = ""

    def generate_Label(instruction: IRLabel) -> str:
        # Implementation to be filled in
        returnstr = f"{instruction.name}"
        return returnstr

    def generate_Jump(instruction: IRJump) -> str:
        # Implementation to be filled in
        returnstr = f"jp {instruction.label}"
        return returnstr

    def generate_CondJump(instruction: IRCondJump) -> str:
        # Implementation to be filled in
        returnstr = ""

    def generate_Call(instruction: IRCall) -> str:
        # Implementation to be filled in
        returnstr = ""
        returnstr += f"call PenguinPush\n"
        #Placer variables
        #Call den reele funktion
        #Result er i A
        returnstr += f"call PenguinPop\n"

    def generate_Return(instruction: IRReturn) -> str:
        # Implementation to be filled in
        returnstr = ""

    def generate_IndexedLoad(instruction: IRIndexedLoad) -> str:
        # Implementation to be filled in
        returnstr = ""

    def generate_IndexedStore(instruction: IRIndexedStore) -> str:
        # Implementation to be filled in
        returnstr = ""

    def generate_HardwareRead(instruction: IRHardwareRead) -> str:
        # Implementation to be filled in
        returnstr = ""

    def generate_HardwareWrite(instruction: IRHardwareWrite) -> str:
        # Implementation to be filled in
        returnstr = ""

    def generate_HardwareIndexedRead(instruction: IRHardwareIndexedRead) -> str:
        # Implementation to be filled in
        returnstr = ""

    def generate_HardwareIndexedWrite(instruction: IRHardwareIndexedWrite) -> str:
        # Implementation to be filled in
        returnstr = ""

    def generate_HardwareCall(instruction: IRHardwareCall) -> str:
        # Implementation to be filled in
        returnstr = ""

    def generate_HardwareMemCpy(instruction: IRHardwareMemCpy) -> str:
        # Implementation to be filled in
        returnstr = ""

    def generate_ArgLoad(instruction: IRArgLoad) -> str:
        # Implementation to be filled in
        returnstr = ""
        return "; Arg was loaded"