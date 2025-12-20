// Coded with the help of GPT (was too tiring)

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
POINTER_BASE = 3  # 3 = THIS, 4 = THAT


class VMTranslator:
    def __init__(self, filename):
        self.filename = filename
        self.filebase = os.path.splitext(os.path.basename(filename))[0]
        self.output = []
        self.label_id = 0

    def unique_label(self, base):
        self.label_id += 1
        return f"{base}.{self.label_id}"

    # ---------------- Stack helpers ----------------
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

    # ---------------- Arithmetic ----------------
    def write_arithmetic(self, cmd):
        if cmd in {"add", "sub", "and", "or"}:
            self.pop_to_d()
            self.output += [
                "@SP", "M=M-1",
                "A=M"
            ]
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
            self.output += [
                "@SP", "M=M-1",
                "A=M", "D=M-D"
            ]

            true_label = self.unique_label("TRUE")
            end_label = self.unique_label("END")

            jump = {
                "eq": "D;JEQ",
                "gt": "D;JGT",
                "lt": "D;JLT"
            }[cmd]

            self.output += [
                f"@{true_label}",
                jump,
                "@SP", "A=M", "M=0",
                f"@{end_label}",
                "0;JMP",
                f"({true_label})",
                "@SP", "A=M", "M=-1",
                f"({end_label})",
                "@SP", "M=M+1"
            ]

    # ---------------- Push ----------------
    def write_push(self, segment, index):
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
            self.output += [
                f"@{TEMP_BASE + index}", "D=M"
            ]
            self.push_d()

        elif segment == "pointer":
            self.output += [
                f"@{POINTER_BASE + index}", "D=M"
            ]
            self.push_d()

        elif segment == "static":
            self.output += [
                f"@{self.filebase}.{index}", "D=M"
            ]
            self.push_d()

    # ---------------- Pop ----------------
    def write_pop(self, segment, index):
        if segment in SEGMENTS:
            base = SEGMENTS[segment]
            self.output += [
                f"@{index}", "D=A",
                f"@{base}", "D=M+D",
                "@R13", "M=D"
            ]
            self.pop_to_d()
            self.output += [
                "@R13", "A=M", "M=D"
            ]

        elif segment == "temp":
            self.pop_to_d()
            self.output += [
                f"@{TEMP_BASE + index}", "M=D"
            ]

        elif segment == "pointer":
            self.pop_to_d()
            self.output += [
                f"@{POINTER_BASE + index}", "M=D"
            ]

        elif segment == "static":
            self.pop_to_d()
            self.output += [
                f"@{self.filebase}.{index}", "M=D"
            ]

    # ---------------- Main ----------------
    def translate(self):
        with open(self.filename) as f:
            lines = f.readlines()

        for line in lines:
            line = line.split("//")[0].strip()
            if not line:
                continue

            parts = line.split()
            cmd = parts[0]

            if cmd in ARITHMETIC:
                self.write_arithmetic(cmd)

            elif cmd == "push":
                self.write_push(parts[1], int(parts[2]))

            elif cmd == "pop":
                self.write_pop(parts[1], int(parts[2]))

        out_file = self.filename.replace(".vm", ".asm")
        with open(out_file, "w") as f:
            f.write("\n".join(self.output))

        print(f"✔ Translated: {out_file}")


# ---------------- Entry ----------------
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python vm_translator.py Xxx.vm")
        sys.exit(1)

    VMTranslator(sys.argv[1]).translate()
