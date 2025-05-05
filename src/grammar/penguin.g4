grammar penguin;

program
    : statement+
    ;

statement
    : declaration
    | assignment
    | initialization
    | conditionalStatement
    | procedureDeclaration
    | returnStatement
    | procedureCallStatement
    | loop
    ;

declaration
    : type name ';'
    ;

assignment
    : name '=' expression ';'
    | listAccess '=' expression ';'
    ;

initialization
    : type name '=' expression ';'
    | 'list' name '=' LBRACK expressions RBRACK ';'
    ;

expression
    : expr_val                              // En value
    | ('-' | '+') expression                // Unary plus/minus
    | '~' expression                        // Unary bitwise not
    | 'not' expression                      // Unary logical not
    | expression ('*') expression           // Gange
    | expression ('+' | '-') expression     // Plus og minus
    | expression ('<<' | '>>') expression   // Bitwise shift operationer
    | expression ('<' | '>' | '<=' | '>=') expression // Comparison operationer - relationer
    | expression ('==' | '!=') expression   // Lighed og ulighed - relationer
    | expression '&' expression             // Bitwise and 
    | expression '^' expression             // Bitwise xor
    | expression '|' expression             // Bitwise or
    | expression 'and' expression           // Logisk and
    | expression 'or' expression            // Logisk or
    ;

expr_val
    : literal           // numre
    | name              // variabler
    | listAccess        // værdier i lister
    | procedureCall     // værdi af procedure
    | attributeAccess   // værdi af attribut i struct
    | LPAREN expression RPAREN // parenteser
    ;

expressions
    : expression (',' expression)*
    ;

listAccess
    : name (LBRACK expression RBRACK)+
    ;

attributeAccess
    : name '.' IDENTIFIER
    ;

conditionalStatement
    : 'if' LPAREN expression RPAREN statementBlock conditionalStatementElse?
    ;

conditionalStatementElse
    : 'else' statementBlock
    ;

procedureDeclaration
    : 'procedure' (type)? IDENTIFIER LPAREN parameterList? RPAREN statementBlock
    ;

procedureCall
    : name LPAREN argumentList? RPAREN
    ;

parameterList
    : type IDENTIFIER (',' type IDENTIFIER)*
    ;

argumentList
    : expression (',' expression)*
    ;

returnStatement
    : 'return' expression ';'
    ;

procedureCallStatement
    : procedureCall ';'
    ;

loop
    : 'loop' LPAREN expression RPAREN statementBlock
    ;

statementBlock
    : LBRACE statement* RBRACE
    ;

name
    : IDENTIFIER ('.' IDENTIFIER | LBRACK expression RBRACK)*
    ;

literal
    : DECIMAL
    | HEX
    | BINARY
    | STRING
    ;

type
    : 'int'
    | 'sprite'
    | 'tileset'
    | 'tilemap'
    ;

comment
    : COMMENT
    ;

// Lexer Rules
LPAREN          : '(';
RPAREN          : ')';
LBRACK          : '[';
RBRACK          : ']';
LBRACE          : '{';
RBRACE          : '}';
//DOT             : '.';
//COMMA           : ',';
//SEMICOLON       : ';';
//ASSIGN          : '=';

//EQUAL           : '==';
//NOTEQUAL        : '!=';
//LE              : '<=';
//GE              : '>=';
//GT              : '>';
//LT              : '<';
//PLUS             : '+';
//MINUS            : '-';
//MUL             : '*';
//LSHIFT          : '<<';
//RSHIFT          : '>>';
//BAND             : '&';
//BOR             : '|';
//BXOR            : '^';
//BCOM             : '~';
//AND            : 'and';
//OR             : 'or';
//NOT            : 'not';

//INT            : 'int';
//SPRITE         : 'sprite';
//TILESET        : 'tileset';
//TILEMAP       : 'tilemap';

IDENTIFIER
    : [a-zA-Z_][a-zA-Z0-9_]*
    ;

DECIMAL
    : [0-9]+
    ;

HEX
    : '0x' [0-9a-fA-F]+
    ;

BINARY
    : '0b' [01]+
    ;

STRING
    : '"' .*? '"'
    ;

COMMENT
    : '//' ~[\r\n]* -> skip
    ;


WS
    : [ \t\r\n]+ -> skip
    ;