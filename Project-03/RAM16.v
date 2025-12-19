// We implement this module using the RAM8 module

module RAM64 (input  wire [15:0] in, input  wire load,input  wire clk,input  wire [5:0]  address, output wire [15:0] out);

    wire [15:0] ram[7:0];

    genvar i;
    generate
        for (i = 0; i < 8; i = i + 1) begin
            RAM8 ram8_i (
                .in(in),
                .load(load & (address[5:3] == i)),
                .clk(clk),
                .address(address[2:0]),
                .out(ram[i])
            );
        end
    endgenerate

    assign out = ram[address[5:3]];

endmodule
