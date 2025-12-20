// Fill.asm
// Blackens screen when key is pressed, clears when not pressed

(LOOP)
@KBD
D=M
@BLACK
D;JNE          // if key pressed - BLACK
@WHITE
0;JMP          // else - WHITE

(BLACK)
@SCREEN
D=A
@ADDR
M=D            // ADDR = SCREEN

(BLACK_LOOP)
@ADDR
D=M
@24576
D=A-D
@LOOP
D;JEQ          // if ADDR == KBD, done

@ADDR
A=M
M=-1           // black pixel

@ADDR
M=M+1
@BLACK_LOOP
0;JMP

(WHITE)
@SCREEN
D=A
@ADDR
M=D            // ADDR = SCREEN

(WHITE_LOOP)
@ADDR
D=M
@24576
D=A-D
@LOOP
D;JEQ          // if ADDR == KBD, done

@ADDR
A=M
M=0            // white pixel

@ADDR
M=M+1
@WHITE_LOOP
0;JMP
