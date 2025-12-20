// Coded with the assistance of GPT

import sys
import os

ARITHMETIC = {
    "add", "sub", "neg",
    "eq", "gt", "lt",
    "and", "or", "not"
}

SEGMENTS = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT"
}

TEMP_BASE = 5
POINTER_BASE = 3  # THIS=3, THAT=4


class VMTranslator:
    def __init__(self, files):
        self.files = files
        self.output = []
        self.label_id = 0
        self.current_function = ""
        self.write_bootstrap = len(files) > 1

        if self.write_bootstrap:
            self.bootstrap()

    # -------------------------------------------------
    # Utilities
    # -------------------------------------------------
    def unique_label(self, base):
        self.label_id += 1
        return f"{base}${self.label_id}"

    def scoped_label(self, label):
        return f"{self.current_function}${label}"

    # -------------------------------------------------
    # Bootstrap
    # -------------------------------------------------
    def bootstrap(self):
        self.output += [
            "// bootstrap",
            "@256", "D=A",
            "@SP", "M=D"
        ]
        self.write_call("Sys.init", 0)

    # -------------------------------------------------
    # Stack helpers
    # -------------------------------------------------
    def push_d(self):
        self.output += [
            "@SP", "A=M", "M=D",
            "@SP", "M=M+1"
        ]

    def pop_to_d(self):
        self.output += [
            "@SP", "M=M-1",
            "A=M", "D=M"
        ]

    # -------------------------------------------------
    # Arithmetic
    # -------------------------------------------------
    def write_arithmetic(self, cmd):
        if cmd in {"add", "sub", "and", "or"}:
            self.pop_to_d()
            self.output += ["@SP", "M=M-1", "A=M"]
            op = {
                "add": "M=M+D",
                "sub": "M=M-D",
                "and": "M=M&D",
                "or":  "M=M|D"
            }[cmd]
            self.output.append(op)
            self.output += ["@SP", "M=M+1"]

        elif cmd in {"neg", "not"}:
            self.output += [
                "@SP", "A=M-1",
                "M=" + ("-M" if cmd == "neg" else "!M")
            ]

        elif cmd in {"eq", "gt", "lt"}:
            self.pop_to_d()
            self.output += ["@SP", "M=M-1", "A=M", "D=M-D"]

            true_label = self.unique_label("TRUE")
            end_label = self.unique_label("END")

            jump = {
                "eq": "D;JEQ",
                "gt": "D;JGT",
                "lt": "D;JLT"
            }[cmd]

            self.output += [
                f"@{true_label}", jump,
                "@SP", "A=M", "M=0",
                f"@{end_label}", "0;JMP",
                f"({true_label})",
                "@SP", "A=M", "M=-1",
                f"({end_label})",
                "@SP", "M=M+1"
            ]

    # -------------------------------------------------
    # Push / Pop
    # -------------------------------------------------
    def write_push(self, segment, index, filebase):
        if segment == "constant":
            self.output += [f"@{index}", "D=A"]
            self.push_d()

        elif segment in SEGMENTS:
            base = SEGMENTS[segment]
            self.output += [
                f"@{index}", "D=A",
                f"@{base}", "A=M+D", "D=M"
            ]
            self.push_d()

        elif segment == "temp":
            self.output += [f"@{TEMP_BASE + index}", "D=M"]
            self.push_d()

        elif segment == "pointer":
            self.output += [f"@{POINTER_BASE + index}", "D=M"]
            self.push_d()

        elif segment == "static":
            self.output += [f"@{filebase}.{index}", "D=M"]
            self.push_d()

    def write_pop(self, segment, index, filebase):
        if segment in SEGMENTS:
            base = SEGMENTS[segment]
            self.output += [
                f"@{index}", "D=A",
                f"@{base}", "D=M+D",
                "@R13", "M=D"
            ]
            self.pop_to_d()
            self.output += ["@R13", "A=M", "M=D"]

        elif segment == "temp":
            self.pop_to_d()
            self.output += [f"@{TEMP_BASE + index}", "M=D"]

        elif segment == "pointer":
            self.pop_to_d()
            self.output += [f"@{POINTER_BASE + index}", "M=D"]

        elif segment == "static":
            self.pop_to_d()
            self.output += [f"@{filebase}.{index}", "M=D"]

    # -------------------------------------------------
    # Branching
    # -------------------------------------------------
    def write_label(self, label):
        self.output.append(f"({self.scoped_label(label)})")

    def write_goto(self, label):
        self.output += [
            f"@{self.scoped_label(label)}",
            "0;JMP"
        ]

    def write_if(self, label):
        self.pop_to_d()
        self.output += [
            f"@{self.scoped_label(label)}",
            "D;JNE"
        ]

    # -------------------------------------------------
    # Functions
    # -------------------------------------------------
    def write_function(self, name, nlocals):
        self.current_function = name
        self.output.append(f"({name})")
        for _ in range(nlocals):
            self.output += ["@0", "D=A"]
            self.push_d()

    def write_call(self, name, nargs):
        ret = self.unique_label("RET")

        # push return address
        self.output += [f"@{ret}", "D=A"]
        self.push_d()

        # save LCL, ARG, THIS, THAT
        for seg in ["LCL", "ARG", "THIS", "THAT"]:
            self.output += [f"@{seg}", "D=M"]
            self.push_d()

        # ARG = SP - 5 - nargs
        self.output += [
            "@SP", "D=M",
            f"@{5 + nargs}", "D=D-A",
            "@ARG", "M=D"
        ]

        # LCL = SP
        self.output += ["@SP", "D=M", "@LCL", "M=D"]

        # goto function
        self.output += [f"@{name}", "0;JMP"]

        # return label
        self.output.append(f"({ret})")

    def write_return(self):
        # FRAME = LCL
        self.output += ["@LCL", "D=M", "@R13", "M=D"]

        # RET = *(FRAME - 5)
        self.output += [
            "@5", "A=D-A", "D=M",
            "@R14", "M=D"
        ]

        # *ARG = pop()
        self.pop_to_d()
        self.output += ["@ARG", "A=M", "M=D"]

        # SP = ARG + 1
        self.output += ["@ARG", "D=M+1", "@SP", "M=D"]

        # restore THAT, THIS, ARG, LCL
        for i, seg in enumerate(["THAT", "THIS", "ARG", "LCL"], 1):
            self.output += [
                "@R13", "D=M",
                f"@{i}", "A=D-A", "D=M",
                f"@{seg}", "M=D"
            ]

        # goto RET
        self.output += ["@R14", "A=M", "0;JMP"]

    # -------------------------------------------------
    # Main
    # -------------------------------------------------
    def translate(self):
        for file in self.files:
            filebase = os.path.splitext(os.path.basename(file))[0]
            with open(file) as f:
                for line in f:
                    line = line.split("//")[0].strip()
                    if not line:
                        continue

                    parts = line.split()
                    cmd = parts[0]

                    if cmd in ARITHMETIC:
                        self.write_arithmetic(cmd)
                    elif cmd == "push":
                        self.write_push(parts[1], int(parts[2]), filebase)
                    elif cmd == "pop":
                        self.write_pop(parts[1], int(parts[2]), filebase)
                    elif cmd == "label":
                        self.write_label(parts[1])
                    elif cmd == "goto":
                        self.write_goto(parts[1])
                    elif cmd == "if-goto":
                        self.write_if(parts[1])
                    elif cmd == "function":
                        self.write_function(parts[1], int(parts[2]))
                    elif cmd == "call":
                        self.write_call(parts[1], int(parts[2]))
                    elif cmd == "return":
                        self.write_return()

        return self.output


# -------------------------------------------------
# Entry
# -------------------------------------------------
if __name__ == "__main__":
    path = sys.argv[1]

    if os.path.isdir(path):
        files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".vm")]
        out = os.path.join(path, os.path.basename(path) + ".asm")
    else:
        files = [path]
        out = path.replace(".vm", ".asm")

    translator = VMTranslator(files)
    asm = translator.translate()

    with open(out, "w") as f:
        f.write("\n".join(asm))

    print(f"✔ Generated {out}")
