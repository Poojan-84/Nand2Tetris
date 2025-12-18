module ALU (input  wire [15:0] x, input  wire [15:0] y,
    input  wire zx,
    input  wire nx,
    input  wire zy,
    input  wire ny,
    input  wire f,
    input  wire no,
            output wire [15:0] out,output wire zr, output wire ng
);

    wire [15:0] x1, x2;
    wire [15:0] y1, y2;
    wire [15:0] out_f;
    wire [15:0] out_n;

    // Zeroing
    assign x1 = zx ? 16'd0 : x;
    assign y1 = zy ? 16'd0 : y;

    // Negation
    assign x2 = nx ? ~x1 : x1;
    assign y2 = ny ? ~y1 : y1;

    // Function selection
    assign out_f = f ? (x2 + y2) : (x2 & y2);

    // Output negation
    assign out = no ? ~out_f : out_f;
  
    // flags
    assign zr = (out == 16'd0);
    assign ng = out[15];   // MSB = sign bit (2’s complement)

endmodule
