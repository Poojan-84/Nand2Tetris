module CPU (
    input  wire [15:0] inM,   // Memory input
    input  wire [15:0] instruction,  // Current instruction
    input  wire reset,
    input  wire clk,

    output wire [15:0] outM   // Memory output
    output wire writeM,         // Write enable
    output wire [14:0] addressM,    // Memory address
    output wire [14:0] pc   // Program counter
);

    // Registers
    reg [15:0] A;
    reg [15:0] D;
    reg [14:0] PC;

    // Instruction fields
    wire isC = instruction[15];
    wire [15:0] A_in = instruction;

    wire zx = instruction[11];
    wire nx = instruction[10];
    wire zy = instruction[9];
    wire ny = instruction[8];
    wire f  = instruction[7];
    wire no = instruction[6];

    wire dA = instruction[5];
    wire dD = instruction[4];
    wire dM = instruction[3];

    wire j1 = instruction[2];
    wire j2 = instruction[1];
    wire j3 = instruction[0];

    // ALU inputs
    wire [15:0] x = D;
    wire [15:0] y = instruction[12] ? inM : A;

    wire [15:0] alu_out;
    wire zr, ng;

    // ALU
    ALU alu (
        .x(x), .y(y),
        .zx(zx), .nx(nx),
        .zy(zy), .ny(ny),
        .f(f), .no(no),
        .out(alu_out),
        .zr(zr),
        .ng(ng)
    );

    // outputs
    assign outM = alu_out;
    assign writeM = isC & dM;
    assign addressM = A[14:0];

    // Jump logic
    wire jump =
        (j1 & ~ng & ~zr) |   // JGT
        (j2 & zr)        |   // JEQ
        (j3 & ng);           // JLT

    // Sequential logic
    always @(posedge clk) begin
        // A-register
        if (!isC)
            A <= A_in;
        else if (dA)
            A <= alu_out;

        // D-register
        if (isC && dD)
            D <= alu_out;

        // PC
        if (reset)
            PC <= 15'd0;
        else if (isC && jump)
            PC <= A[14:0];
        else
            PC <= PC + 1;
    end

    assign pc = PC;

endmodule
