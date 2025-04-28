from RegisterAllocater import RegisterAllocator
from ast_classes import ASTNode, ProcedureCall, BinaryOp, UnaryOp, IntegerLiteral, StringLiteral, Variable, ListAccess

#NEED TO IMPLEMENT BINARY IMPORTING
#NEED TO IMPLEMENT LIST HANDLING



class CodeGenerator:
    """Generates GameBoy Z80 assembly code from Penguin AST."""
    
    def __init__(self):
        self.register_allocator = RegisterAllocator()
        self.code = []
        self.label_counter = 0
        self.current_scope = "global"
        self.var_types = {}  # Track variable types
        
    def generate(self, ast_node):
        """Entry point for code generation."""
        self.emit_header()
        self.visit(ast_node)
        self.emit_footer()
        return '\n'.join(self.code)
    
    def emit(self, instruction):
        """Add an instruction to the output code."""
        self.code.append(instruction)
    
    def emit_header(self):
        """Emit the header section of the GameBoy ROM."""
        self.emit("; GameBoy ROM generated from Penguin language")
        self.emit("SECTION \"ROM0\", ROM0")
        self.emit("INCLUDE \"hardware.inc\"")  # Common GB hardware definitions
        
        # ROM header
        self.emit("\nSECTION \"Header\", ROM0[$100]")
        self.emit("    jp EntryPoint")
        self.emit("    ds $150 - @, 0  ; Make room for the header")
        
        # Program entry point
        self.emit("\nEntryPoint:")
        self.emit("    di  ; Disable interrupts")
        self.emit("    ld sp, $FFFE  ; Set stack pointer")
        self.emit("    call Main")
        self.emit("    jp Halt")
    
    def emit_footer(self):
        """Emit the footer section of the GameBoy ROM."""
        self.emit("\nHalt:")
        self.emit("    halt")
        self.emit("    jp Halt")

    def new_label(self, prefix="label"):
        """Generate a new unique label."""
        self.label_counter += 1
        return f"{prefix}_{self.label_counter}"
    
    def visit(self, node):
        """Generic visitor that dispatches to specific visitor methods."""
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, None)
    
        if visitor is None:
            raise ValueError(f"No visitor method found for {type(node).__name__}")
    
        return visitor(node)
    
    # Visit methods for each AST node type
    
    def visit_Program(self, node):
        """Visit Program node."""
        # Create main function
        self.emit("\nMain:")
        
        # Process all statements
        for statement in node.statements:
            self.visit(statement)
        
        # Return from main
        self.emit("    ret")

    def visit_Declaration(self, node):
    def visit_Assignment(self, node):
    def visit_Initialization(self, node):
    def visit_ListInitialization(self, node):
    def visit_Conditional(self, node):
    def visit_Loop(self, node):
    def visit_ProcedureDef(self, node):     
    def visit_Return(self, node):
    def visit_ProcedureCall(self, node):        
    def visit_BinaryOp(self, node):
    def visit_UnaryOp(self, node):      
    def visit_IntegerLiteral(self, node):
    def visit_StringLiteral(self, node):
    def visit_Variable(self, node):     
    def visit_ListAccess(self, node):
    def visit_AttributeAccess(self, node):
    def visit_ProcedureCallStatement(self, node):
    def visit_Expression(self, node):