//built over RAM4K module, 8X4K.

module RAM16K (
    input  wire [15:0] in,
    input  wire load,
    input  wire clk,
    input  wire [13:0] address,
    output wire [15:0] out
);

    wire [15:0] ram[3:0];

    genvar i;
    generate
        for (i = 0; i < 4; i = i + 1) begin
            RAM4K ram4k_i (
                .in(in),
              .load(load & (address[13:12] == i)),  //added the extra address bits(k), over the 4K address bits
                .clk(clk),
                .address(address[11:0]),
                .out(ram[i])
            );
        end
    endgenerate

    assign out = ram[address[13:12]];

endmodule
