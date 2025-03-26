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
    : literal
    | name
    | listAccess
    | attributeAccess
    | procedureCall
    | '(' expression ')'
    | 'not' expression
    | '~' expression
    | expression comparisonOperator expression
    | expression arithmeticOperator expression
    | expression logicalOperator expression
    | expression bitwiseOperator expression
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

comparisonOperator
    : '==' | '!=' | '<' | '>' | '<=' | '>='
    ;

arithmeticOperator
    : '+' | '-' | '*'
    ;

logicalOperator
    : 'and' | 'or' | 'xor'
    ;
    
bitwiseOperator
    : '&' | '|'| '<<' | '>>'
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