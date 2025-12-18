module inc16 (
    input  wire [15:0] in,
    output wire [15:0] out
);
    wire [16:0] carry;
  assign carry[0] = 1'b1;   // +1

    genvar i;
    generate
        for (i = 0; i < 16; i = i + 1) begin
            assign out[i] = in[i] ^ carry[i];
            assign carry[i+1] = in[i] & carry[i];
        end
    endgenerate
endmodule
//Hmmm
