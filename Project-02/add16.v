module add16 (input  wire [15:0] a, input  wire [15:0] b, output wire [15:0] sum
);
    wire [16:0] carry;
    assign carry[0] = 1'b0;

    genvar i;
    generate
        for (i = 0; i < 16; i = i + 1) begin
            assign sum[i]   = a[i] ^ b[i] ^ carry[i];
            assign carry[i+1] = (a[i] & b[i]) |
                                (a[i] & carry[i]) |
                                (b[i] & carry[i]);
        end
    endgenerate
endmodule
