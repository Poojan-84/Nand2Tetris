// Implemented using the RAM64 module

module RAM512 (
    input  wire [15:0] in,
    input  wire load,
    input  wire clk,
    input  wire [8:0]  address,
    output wire [15:0] out
);

    wire [15:0] ram[7:0];

    genvar i;
    generate
        for (i = 0; i < 8; i = i + 1) begin
            RAM64 ram64_i (
                .in(in),
              .load(load & (address[8:6] == i)),  //added the additional address(k) values over the existing 6 address values of RAM64 
                .clk(clk),
                .address(address[5:0]),
                .out(ram[i])
            );
        end
    endgenerate

    assign out = ram[address[8:6]];

endmodule
