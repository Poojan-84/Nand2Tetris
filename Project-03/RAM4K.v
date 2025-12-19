//implemented using the RAM512 module, 8X512

module RAM4K (
    input  wire [15:0] in,
    input  wire load,
    input  wire clk,
    input  wire [11:0] address,
    output wire [15:0] out
);

    wire [15:0] ram[7:0];

    genvar i;
    generate
        for (i = 0; i < 8; i = i + 1) begin
            RAM512 ram512_i (
                .in(in),
              .load(load & (address[11:9] == i)), //added the additional k(address) values over the existing ones
                .clk(clk),
                .address(address[8:0]),
                .out(ram[i])
            );
        end
    endgenerate

    assign out = ram[address[11:9]];

endmodule
