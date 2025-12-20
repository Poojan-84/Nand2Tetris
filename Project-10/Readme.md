1) JackTokenizer

Removes comments

Splits input into tokens

- Classifies tokens:
keyword, 
symbol, 
identifier, 
integerConstant, 
stringConstant


2) CompilationEngine

Consumes tokens

Implements Jack grammar rules:
class, 
classVarDec, 
subroutineDec, 
statements, 
expressions, 
terms

Emits XML parse tree
