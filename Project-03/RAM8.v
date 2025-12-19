// To implement this module we have utilized the register16 module

module RAM8(input wire in, input wire clk, input wire load, input wire [2:0] address, output wire [15:0] out);

  wire [15:0] r[7:0];

  genvar i;
  generate
    for(i=0;i<8;i=i+1) begin
      register16 reg_i (
        .in(in),
        .(load & (address == i)),
        .clk(clk),
        .out(r[i])
      );
    end
  endgenerate

  assign out = r[address];
endmodule
  
    
