import sys, os, re

# -------------------------------------------------
# Symbol Table
# -------------------------------------------------
class SymbolTable:
    def __init__(self):
        self.class_scope = {}
        self.sub_scope = {}
        self.counts = {"static":0,"field":0,"arg":0,"var":0}

    def start_subroutine(self):
        self.sub_scope = {}
        self.counts["arg"] = 0
        self.counts["var"] = 0

    def define(self, name, type_, kind):
        index = self.counts[kind]
        self.counts[kind] += 1
        table = self.class_scope if kind in ("static","field") else self.sub_scope
        table[name] = (type_, kind, index)

    def var_count(self, kind):
        return self.counts[kind]

    def kind_of(self, name):
        if name in self.sub_scope: return self.sub_scope[name][1]
        if name in self.class_scope: return self.class_scope[name][1]
        return None

    def type_of(self, name):
        if name in self.sub_scope: return self.sub_scope[name][0]
        if name in self.class_scope: return self.class_scope[name][0]
        return None

    def index_of(self, name):
        if name in self.sub_scope: return self.sub_scope[name][2]
        if name in self.class_scope: return self.class_scope[name][2]
        return None

# -------------------------------------------------
# VM Writer
# -------------------------------------------------
class VMWriter:
    def __init__(self, out):
        self.out = out

    def write(self, s): self.out.write(s+"\n")
    def push(self, seg, idx): self.write(f"push {seg} {idx}")
    def pop(self, seg, idx): self.write(f"pop {seg} {idx}")
    def arithmetic(self, cmd): self.write(cmd)
    def label(self, l): self.write(f"label {l}")
    def goto(self, l): self.write(f"goto {l}")
    def if_goto(self, l): self.write(f"if-goto {l}")
    def call(self, n, k): self.write(f"call {n} {k}")
    def function(self, n, k): self.write(f"function {n} {k}")
    def ret(self): self.write("return")

# -------------------------------------------------
# Tokenizer (same as Project 10)
# -------------------------------------------------
KEYWORDS = {
    "class","constructor","function","method","field","static","var",
    "int","char","boolean","void","true","false","null","this",
    "let","do","if","else","while","return"
}
SYMBOLS = set("{}()[].,;+-*/&|<>=~")

class Tokenizer:
    def __init__(self, src):
        src = re.sub(r"//.*|/\*[\s\S]*?\*/","",src)
        self.tokens = re.findall(r'"[^"]*"|\w+|['+re.escape("".join(SYMBOLS))+']',src)
        self.i = 0

    def peek(self): return self.tokens[self.i]
    def advance(self): self.i += 1; return self.tokens[self.i-1]
    def has(self): return self.i < len(self.tokens)

# -------------------------------------------------
# Compilation Engine (FULL)
# -------------------------------------------------
class CompilationEngine:
    def __init__(self, tk, vm):
        self.tk = tk
        self.vm = vm
        self.st = SymbolTable()
        self.class_name = ""
        self.label_id = 0
        self.compile_class()

    def new_label(self, base):
        self.label_id += 1
        return f"{base}{self.label_id}"

    def eat(self): return self.tk.advance()

    # ---------- class ----------
    def compile_class(self):
        self.eat()                  # class
        self.class_name = self.eat()
        self.eat()                  # {

        while self.tk.peek() in ("static","field"):
            self.compile_class_var()

        while self.tk.peek() in ("constructor","function","method"):
            self.compile_subroutine()

        self.eat()                  # }

    def compile_class_var(self):
        kind = self.eat()
        type_ = self.eat()
        while True:
            name = self.eat()
            self.st.define(name,type_,kind)
            if self.tk.peek() != ",": break
            self.eat()
        self.eat()

    # ---------- subroutine ----------
    def compile_subroutine(self):
        self.st.start_subroutine()
        sub_type = self.eat()
        self.eat()  # return type
        name = self.eat()

        if sub_type == "method":
            self.st.define("this",self.class_name,"arg")

        self.eat()  # (
        self.compile_params()
        self.eat()  # )

        self.eat()  # {
        while self.tk.peek()=="var":
            self.compile_var()

        self.vm.function(f"{self.class_name}.{name}",self.st.var_count("var"))

        if sub_type=="constructor":
            self.vm.push("constant",self.st.var_count("field"))
            self.vm.call("Memory.alloc",1)
            self.vm.pop("pointer",0)
        elif sub_type=="method":
            self.vm.push("argument",0)
            self.vm.pop("pointer",0)

        self.compile_statements()
        self.eat()  # }

    def compile_params(self):
        if self.tk.peek()==")": return
        while True:
            t = self.eat()
            n = self.eat()
            self.st.define(n,t,"arg")
            if self.tk.peek() != ",": break
            self.eat()

    def compile_var(self):
        self.eat()
        t = self.eat()
        while True:
            n = self.eat()
            self.st.define(n,t,"var")
            if self.tk.peek() != ",": break
            self.eat()
        self.eat()

    # ---------- statements ----------
    def compile_statements(self):
        while self.tk.peek() in ("let","if","while","do","return"):
            getattr(self,"compile_"+self.tk.peek())()

    def compile_let(self):
        self.eat()
        name = self.eat()
        is_array = False
        if self.tk.peek()=="[":
            is_array=True
            self.push_var(name)
            self.eat()
            self.compile_expr()
            self.eat()
            self.vm.arithmetic("add")

        self.eat()
        self.compile_expr()
        self.eat()

        if is_array:
            self.vm.pop("temp",0)
            self.vm.pop("pointer",1)
            self.vm.push("temp",0)
            self.vm.pop("that",0)
        else:
            self.pop_var(name)

    def compile_if(self):
        self.eat()
        l1,l2 = self.new_label("IF"),self.new_label("ENDIF")
        self.eat()
        self.compile_expr()
        self.eat()
        self.vm.arithmetic("not")
        self.vm.if_goto(l1)
        self.eat()
        self.compile_statements()
        self.eat()
        if self.tk.peek()=="else":
            self.vm.goto(l2)
            self.vm.label(l1)
            self.eat()
            self.eat()
            self.compile_statements()
            self.eat()
            self.vm.label(l2)
        else:
            self.vm.label(l1)

    def compile_while(self):
        self.eat()
        l1,l2 = self.new_label("WHILE"),self.new_label("ENDWHILE")
        self.vm.label(l1)
        self.eat()
        self.compile_expr()
        self.eat()
        self.vm.arithmetic("not")
        self.vm.if_goto(l2)
        self.eat()
        self.compile_statements()
        self.eat()
        self.vm.goto(l1)
        self.vm.label(l2)

    def compile_do(self):
        self.eat()
        self.compile_call()
        self.vm.pop("temp",0)
        self.eat()

    def compile_return(self):
        self.eat()
        if self.tk.peek()!=";":
            self.compile_expr()
        else:
            self.vm.push("constant",0)
        self.eat()
        self.vm.ret()

    # ---------- expressions ----------
    def compile_expr(self):
        self.compile_term()
        while self.tk.peek() in "+-*/&|<>=":
            op = self.eat()
            self.compile_term()
            self.vm.arithmetic({
                "+":"add","-":"sub","&":"and","|":"or",
                "<":"lt",">":"gt","=":"eq"
            }.get(op, "call Math.multiply 2"))

    def compile_term(self):
        tok = self.tk.peek()
        if tok.isdigit():
            self.vm.push("constant",int(self.eat()))
        elif tok=="(":
            self.eat(); self.compile_expr(); self.eat()
        elif tok in "-~":
            op=self.eat(); self.compile_term()
            self.vm.arithmetic("neg" if op=="-" else "not")
        else:
            name = self.eat()
            if self.tk.peek()=="[":
                self.push_var(name)
                self.eat()
                self.compile_expr()
                self.eat()
                self.vm.arithmetic("add")
                self.vm.pop("pointer",1)
                self.vm.push("that",0)
            elif self.tk.peek() in (".","("):
                self.compile_call(name)
            else:
                self.push_var(name)

    # ---------- helpers ----------
    def compile_call(self, name=None):
        if name is None:
            name = self.eat()
        n_args = 0
        if self.tk.peek()==".":
            self.eat()
            sub = self.eat()
            kind = self.st.kind_of(name)
            if kind:
                self.push_var(name)
                name = f"{self.st.type_of(name)}.{sub}"
                n_args = 1
            else:
                name = f"{name}.{sub}"
        else:
            self.vm.push("pointer",0)
            name = f"{self.class_name}.{name}"
            n_args = 1

        self.eat()
        if self.tk.peek()!=")":
            n_args += self.compile_expr_list()
        self.eat()
        self.vm.call(name,n_args)

    def compile_expr_list(self):
        c = 0
        while True:
            self.compile_expr()
            c += 1
            if self.tk.peek() != ",": break
            self.eat()
        return c

    def push_var(self,name):
        seg = {"static":"static","field":"this","arg":"argument","var":"local"}[self.st.kind_of(name)]
        self.vm.push(seg,self.st.index_of(name))

    def pop_var(self,name):
        seg = {"static":"static","field":"this","arg":"argument","var":"local"}[self.st.kind_of(name)]
        self.vm.pop(seg,self.st.index_of(name))

# -------------------------------------------------
# Driver
# -------------------------------------------------
def compile_path(path):
    files=[]
    if os.path.isdir(path):
        files=[os.path.join(path,f) for f in os.listdir(path) if f.endswith(".jack")]
    else:
        files=[path]

    for f in files:
        with open(f) as src, open(f.replace(".jack",".vm"),"w") as out:
            CompilationEngine(Tokenizer(src.read()), VMWriter(out))
        print(f"✔ Compiled {f}")

if __name__=="__main__":
    compile_path(sys.argv[1])
