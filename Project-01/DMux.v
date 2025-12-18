module dmux (input wire a, output wire b, input wire sel, output wire c);
  assign b = (~sel) & a ;
  assign c = sel & a;
endmodule
