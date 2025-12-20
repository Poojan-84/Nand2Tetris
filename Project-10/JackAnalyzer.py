import sys
import os
import re

# Tokenizer
KEYWORDS = {
    "class","constructor","function","method","field","static","var",
    "int","char","boolean","void","true","false","null","this",
    "let","do","if","else","while","return"
}

SYMBOLS = set("{}()[].,;+-*/&|<>=~")

ESCAPE = {
    "<": "&lt;",
    ">": "&gt;",
    "&": "&amp;"
}

class JackTokenizer:
    def __init__(self, source):
        self.tokens = []
        self.index = 0
        self.tokenize(source)

    def tokenize(self, source):
        source = re.sub(r"//.*|/\*[\s\S]*?\*/", "", source)
        pattern = r'"[^"\n]*"|[A-Za-z_]\w*|\d+|[' + re.escape("".join(SYMBOLS)) + ']'
        self.tokens = re.findall(pattern, source)

    def has_more_tokens(self):
        return self.index < len(self.tokens)

    def advance(self):
        tok = self.tokens[self.index]
        self.index += 1
        return tok

    def peek(self):
        return self.tokens[self.index]

# ----------------------------
# CompilationEngine

class CompilationEngine:
    def __init__(self, tokenizer, out):
        self.tk = tokenizer
        self.out = out
        self.indent = 0
        self.compile_class()

    def write(self, s):
        self.out.write("  " * self.indent + s + "\n")

    def open(self, tag):
        self.write(f"<{tag}>")
        self.indent += 1

    def close(self, tag):
        self.indent -= 1
        self.write(f"</{tag}>")

    def write_token(self, tok):
        if tok in KEYWORDS:
            self.write(f"<keyword> {tok} </keyword>")
        elif tok in SYMBOLS:
            tok = ESCAPE.get(tok, tok)
            self.write(f"<symbol> {tok} </symbol>")
        elif tok.isdigit():
            self.write(f"<integerConstant> {tok} </integerConstant>")
        elif tok.startswith('"'):
            self.write(f"<stringConstant> {tok[1:-1]} </stringConstant>")
        else:
            self.write(f"<identifier> {tok} </identifier>")

    def eat(self):
        self.write_token(self.tk.advance())

    # ---------------- Grammar ----------------

    def compile_class(self):
        self.open("class")
        self.eat()  # class
        self.eat()  # className
        self.eat()  # {

        while self.tk.peek() in ("static","field"):
            self.compile_class_var_dec()

        while self.tk.peek() in ("constructor","function","method"):
            self.compile_subroutine()

        self.eat()  # }
        self.close("class")

    def compile_class_var_dec(self):
        self.open("classVarDec")
        while True:
            self.eat()
            if self.tk.peek() == ";":
                break
        self.eat()
        self.close("classVarDec")

    def compile_subroutine(self):
        self.open("subroutineDec")
        self.eat()
        self.eat()
        self.eat()
        self.eat()  # (
        self.compile_parameter_list()
        self.eat()  # )
        self.compile_subroutine_body()
        self.close("subroutineDec")

    def compile_parameter_list(self):
        self.open("parameterList")
        if self.tk.peek() != ")":
            while True:
                self.eat()
                if self.tk.peek() != ",":
                    break
                self.eat()
        self.close("parameterList")

    def compile_subroutine_body(self):
        self.open("subroutineBody")
        self.eat()  # {
        while self.tk.peek() == "var":
            self.compile_var_dec()
        self.compile_statements()
        self.eat()  # }
        self.close("subroutineBody")

    def compile_var_dec(self):
        self.open("varDec")
        while True:
            self.eat()
            if self.tk.peek() == ";":
                break
        self.eat()
        self.close("varDec")

    def compile_statements(self):
        self.open("statements")
        while self.tk.peek() in ("let","if","while","do","return"):
            getattr(self, f"compile_{self.tk.peek()}")()
        self.close("statements")

    def compile_let(self):
        self.open("letStatement")
        self.eat()
        self.eat()
        if self.tk.peek() == "[":
            self.eat()
            self.compile_expression()
            self.eat()
        self.eat()
        self.compile_expression()
        self.eat()
        self.close("letStatement")

    def compile_if(self):
        self.open("ifStatement")
        self.eat()
        self.eat()
        self.compile_expression()
        self.eat()
        self.eat()
        self.compile_statements()
        self.eat()
        if self.tk.peek() == "else":
            self.eat()
            self.eat()
            self.compile_statements()
            self.eat()
        self.close("ifStatement")

    def compile_while(self):
        self.open("whileStatement")
        self.eat()
        self.eat()
        self.compile_expression()
        self.eat()
        self.eat()
        self.compile_statements()
        self.eat()
        self.close("whileStatement")

    def compile_do(self):
        self.open("doStatement")
        while True:
            self.eat()
            if self.tk.peek() == ";":
                break
        self.eat()
        self.close("doStatement")

    def compile_return(self):
        self.open("returnStatement")
        self.eat()
        if self.tk.peek() != ";":
            self.compile_expression()
        self.eat()
        self.close("returnStatement")

    def compile_expression(self):
        self.open("expression")
        self.compile_term()
        while self.tk.peek() in "+-*/&|<>=":
            self.eat()
            self.compile_term()
        self.close("expression")

    def compile_term(self):
        self.open("term")
        tok = self.tk.peek()
        if tok == "(":
            self.eat()
            self.compile_expression()
            self.eat()
        elif tok in "-~":
            self.eat()
            self.compile_term()
        else:
            self.eat()
            if self.tk.peek() in ("[",".","("):
                self.eat()
                if self.tk.peek() != ")":
                    self.compile_expression()
                while self.tk.peek() == ",":
                    self.eat()
                    self.compile_expression()
                self.eat()
        self.close("term")

# ----------------------------
# Driver
# ----------------------------

def analyze(path):
    files = []
    if os.path.isdir(path):
        files = [os.path.join(path,f) for f in os.listdir(path) if f.endswith(".jack")]
    else:
        files = [path]

    for file in files:
        with open(file) as f:
            source = f.read()

        tokenizer = JackTokenizer(source)
        outname = file.replace(".jack",".xml")

        with open(outname,"w") as out:
            CompilationEngine(tokenizer, out)

        print(f"✔ Parsed {outname}")

if __name__ == "__main__":
    analyze(sys.argv[1])
