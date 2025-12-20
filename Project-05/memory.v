module Memory (
    input  wire [15:0] in,
    input  wire load,
    input  wire clk,
    input  wire [14:0] address,
    output wire [15:0] out
);

    wire [15:0] ram_out;
    wire [15:0] screen_out;
    wire [15:0] keyboard_out;

    // Address decoding
    wire ram_sel     = (address < 15'd16384);
    wire screen_sel  = (address >= 15'd16384 && address < 15'd24576);
    wire keyboard_sel = (address == 15'd24576);

  // Builtin chips (already built these in Project03)
    RAM16K ram (
        .in(in),
        .load(load & ram_sel),
        .clk(clk),
        .address(address[13:0]),
        .out(ram_out)
    );

    Screen screen (
        .in(in),
        .load(load & screen_sel),
        .clk(clk),
        .address(address[12:0]),
        .out(screen_out)
    );

    Keyboard keyboard (
        .out(keyboard_out)
    );

    // Output mux
    assign out = ram_sel ? ram_out :screen_sel ? screen_out : keyboard_out;

endmodule
