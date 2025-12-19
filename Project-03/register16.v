module register16(input wire [15:0] in, input wire load, input wire clk, output reg [15:0] out);

    always @(posedge clk) begin
        if (load)
            out <= in;
        else
            out <= out;   // hold value
    end

endmodule
