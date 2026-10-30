"""Tkinter user interface for the complete MiniLang compiler pipeline."""

import tkinter as tk
from tkinter import ttk

from ast_nodes import (Assignment, BinaryExpression, Boolean, BreakStatement,
                       CompoundAssignment, ContinueStatement, Identifier,
                       IfStatement, Number, PrintStatement, Program, String,
                       UnaryExpression, VariableDeclaration, WhileStatement)
from code_generator import CodeGenerator, format_instructions
from lexer import Lexer
from machine_code import MachineCodeGenerator, VirtualMachine, format_machine_code
from optimizer import Optimizer
from parser import Parser
from semantic import SemanticAnalyzer


DEFAULT_PROGRAM = """// MiniLang demonstration
let age = 20;
let price = 99.50;
let name = \"MiniLang\";
let active = true;

if (age >= 18 && active) {
    print(name + \" is active\");
} else {
    print(\"Inactive\");
}"""


def ast_text(node, indent=0):
    padding = "  " * indent
    if isinstance(node, Program):
        return padding + "Program\n" + "\n".join(ast_text(item, indent + 1) for item in node.statements)
    if isinstance(node, Number):
        return padding + f"Number({node.value!r})"
    if isinstance(node, String):
        return padding + f"String({node.value!r})"
    if isinstance(node, Boolean):
        return padding + f"Boolean({node.value})"
    if isinstance(node, Identifier):
        return padding + f"Identifier({node.name})"
    if isinstance(node, UnaryExpression):
        return padding + f"Unary({node.operator})\n{ast_text(node.operand, indent + 1)}"
    if isinstance(node, BinaryExpression):
        return padding + f"Binary({node.operator})\n{ast_text(node.left, indent + 1)}\n{ast_text(node.right, indent + 1)}"
    if isinstance(node, VariableDeclaration):
        return padding + f"VariableDeclaration({node.name})\n{ast_text(node.initializer, indent + 1)}"
    if isinstance(node, Assignment):
        return padding + f"Assignment({node.name})\n{ast_text(node.value, indent + 1)}"
    if isinstance(node, CompoundAssignment):
        return padding + f"CompoundAssignment({node.name} {node.operator})\n{ast_text(node.value, indent + 1)}"
    if isinstance(node, PrintStatement):
        return padding + "PrintStatement\n" + ast_text(node.expression, indent + 1)
    if isinstance(node, BreakStatement):
        return padding + "BreakStatement"
    if isinstance(node, ContinueStatement):
        return padding + "ContinueStatement"
    if isinstance(node, IfStatement):
        result = padding + "IfStatement\n" + ast_text(node.condition, indent + 1)
        result += "\n" + padding + "  Then\n" + "\n".join(ast_text(item, indent + 2) for item in node.then_branch)
        if node.else_branch is not None:
            result += "\n" + padding + "  Else\n" + "\n".join(ast_text(item, indent + 2) for item in node.else_branch)
        return result
    if isinstance(node, WhileStatement):
        return padding + "WhileStatement\n" + ast_text(node.condition, indent + 1) + "\n" + "\n".join(ast_text(item, indent + 1) for item in node.body)
    return padding + type(node).__name__


class MiniCompilerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MiniLang Compiler Laboratory")
        self.root.geometry("1200x820")
        self.root.minsize(900, 600)
        self.build_widgets()
        self.source_editor.insert("1.0", DEFAULT_PROGRAM)

    def build_widgets(self):
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        outer = ttk.Frame(self.root, padding=12)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="Design and Development of a Mini Compiler for a Sample Programming Language", style="Title.TLabel", wraplength=1100).pack(anchor="w")
        ttk.Label(outer, text="MiniLang | Lexer -> Parser -> Semantic Analysis -> IR -> Optimization -> Machine Code -> Virtual Machine").pack(anchor="w", pady=(3, 8))

        editor_frame = ttk.LabelFrame(outer, text="MiniLang Source Code", padding=6)
        editor_frame.pack(fill="both", expand=True)
        self.source_editor = tk.Text(editor_frame, height=10, undo=True, font=("Consolas", 10), wrap="none")
        self.source_editor.pack(side="left", fill="both", expand=True)
        editor_scroll = ttk.Scrollbar(editor_frame, orient="vertical", command=self.source_editor.yview)
        editor_scroll.pack(side="right", fill="y")
        self.source_editor.configure(yscrollcommand=editor_scroll.set)

        controls = ttk.Frame(outer)
        controls.pack(fill="x", pady=6)
        ttk.Button(controls, text="Compile", command=self.compile_program).pack(side="left")
        ttk.Button(controls, text="Clear", command=self.clear).pack(side="left", padx=6)
        self.status = ttk.Label(controls, text="Ready")
        self.status.pack(side="right")

        results = ttk.Frame(outer)
        results.pack(fill="both", expand=True)
        self.panels = {}
        panel_specs = [
            ("Tokens", "tokens"), ("Syntax / AST", "ast"),
            ("Semantic Analysis", "semantic"), ("Original Intermediate Code", "original_ir"),
            ("Optimization", "optimization"), ("Optimized Intermediate Code", "optimized_ir"),
            ("Machine Code", "machine"), ("Program Output", "output"),
        ]
        for index, (title, key) in enumerate(panel_specs):
            frame = ttk.LabelFrame(results, text=title, padding=4)
            frame.grid(row=index // 2, column=index % 2, sticky="nsew", padx=3, pady=3)
            content = ttk.Frame(frame)
            content.pack(fill="both", expand=True)
            text = tk.Text(content, height=5, width=55, state="disabled", font=("Consolas", 9), wrap="none")
            text.pack(side="left", fill="both", expand=True)
            scrollbar = ttk.Scrollbar(content, orient="vertical", command=text.yview)
            scrollbar.pack(side="right", fill="y")
            text.configure(yscrollcommand=scrollbar.set)
            self.panels[key] = text
        for column in range(2):
            results.columnconfigure(column, weight=1)
        for row in range(4):
            results.rowconfigure(row, weight=1)

    def set_panel(self, key, content):
        panel = self.panels[key]
        panel.configure(state="normal")
        panel.delete("1.0", "end")
        panel.insert("1.0", content)
        panel.configure(state="disabled")

    def clear_panels(self):
        for key in self.panels:
            self.set_panel(key, "")

    def compile_program(self):
        self.clear_panels()
        source = self.source_editor.get("1.0", "end-1c")
        try:
            tokens = Lexer().tokenize(source)
            self.set_panel("tokens", "\n".join(str(token) for token in tokens))
            tree = Parser(tokens).parse()
            self.set_panel("ast", ast_text(tree))
            symbols = SemanticAnalyzer().analyze(tree)
            self.set_panel("semantic", "Semantic analysis passed.\n" + "\n".join(f"{name}: {symbol.type_name}" for name, symbol in symbols.symbols.items()))
            original = CodeGenerator().generate(tree)
            self.set_panel("original_ir", format_instructions(original))
            optimized = Optimizer().optimize(original)
            optimization_text = f"Original instructions: {optimized.original_count}\nOptimized instructions: {len(optimized.instructions)}\nOptimizations applied:\n"
            optimization_text += "\n".join(f"- {item}" for item in optimized.applied) if optimized.applied else "- None"
            self.set_panel("optimization", optimization_text)
            self.set_panel("optimized_ir", format_instructions(optimized.instructions))
            machine = MachineCodeGenerator().generate(optimized.instructions)
            self.set_panel("machine", format_machine_code(machine))
            output, _ = VirtualMachine().execute(machine)
            self.set_panel("output", "\n".join(output) if output else "(program produced no output)")
            self.status.configure(text="Compilation successful")
        except Exception as error:
            self.set_panel("semantic", str(error))
            self.status.configure(text=f"Compilation failed - {getattr(error, 'phase', 'Compiler')} Error")

    def clear(self):
        self.source_editor.delete("1.0", "end")
        self.clear_panels()
        self.status.configure(text="Ready")


def launch():
    root = tk.Tk()
    MiniCompilerApp(root)
    root.mainloop()
