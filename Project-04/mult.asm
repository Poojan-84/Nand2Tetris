// Mult.asm
// Computes R0 * R1 and stores the result in R2

@R2
M=0            // R2 = 0 (result)

@R1
D=M
@COUNT
M=D            // COUNT = R1

(LOOP)
@COUNT
D=M
@END
D;JEQ          // if COUNT == 0, end

@R0
D=M
@R2
M=M+D          // R2 += R0

@COUNT
M=M-1          // COUNT--

@LOOP
0;JMP

(END)
@END
0;JMP          // infinite loop (halt)
