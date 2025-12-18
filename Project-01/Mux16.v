module Mux16 (input wire [15:0] a, input wire [3:0] sel, output wire c);
  assign c = a[sel];
endmodule
    // This one was tough to figure out
