module bit (input wire in, input wire load, output reg out, input wire clk);

always @(posedge clk) begin
    if(load)
        out <=in;
    else
        out<=out;
    end
endmodule
