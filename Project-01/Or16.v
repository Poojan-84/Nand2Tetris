module or16 (input wire [15:0] a, input wire [15:0] b, output wire [15:0] c);
  genvar i;
  generate
    for(i=0;i<16;i = i+1) begin
      assign c[i]=a[i]|b[i];
    end
  endgenerate
endmodule
    
