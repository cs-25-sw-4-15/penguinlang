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
    | 'list' name '=' '[' expressions ']' ';'
    ;

expression
    : expr_val                              // En value
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
    | attributeAccess   // værdi af attribut i struct
    | procedureCall     // værdi af procedure
    | '(' expression ')'// parenteser
    ;

expressions
    : expression (',' expression)*
    ;

listAccess
    : name ('[' expression ']')+
    ;

attributeAccess
    : name '.' IDENTIFIER
    ;

conditionalStatement
    : 'if' '(' expression ')' statementBlock conditionalStatementElse?
    ;

conditionalStatementElse
    : 'else' statementBlock
    ;

procedureDeclaration
    : 'procedure' (type)? IDENTIFIER '(' parameterList? ')' statementBlock
    ;

procedureCall
    : name '(' argumentList? ')'
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
    : 'loop' '(' expression ')' statementBlock
    ;

statementBlock
    : '{' statement* '}'
    ;

name
    : IDENTIFIER ('.' IDENTIFIER | '[' expression ']')*
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