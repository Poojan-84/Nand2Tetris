module mux (input wire a, input wire b, input wire sel, output wire c);
  assign c = sel ? b : a;
endmodule
