"""Phase 4: generate readable three-address-style intermediate code."""

from dataclasses import dataclass

from ast_nodes import (Assignment, BinaryExpression, Boolean, BreakStatement,
                       CompoundAssignment, ContinueStatement, Identifier,
                       IfStatement, Number, PrintStatement, Program, String,
                       UnaryExpression, VariableDeclaration, WhileStatement)


@dataclass(frozen=True)
class Constant:
    value: object

    def __str__(self):
        if isinstance(self.value, str):
            return '"' + self.value.replace('"', '\\"') + '"'
        if isinstance(self.value, bool):
            return str(self.value).lower()
        return str(self.value)


@dataclass
class Instruction:
    operation: str
    arguments: tuple
    line: int = 0

    def __str__(self):
        op = self.operation
        args = self.arguments
        if op == "LABEL":
            return f"{args[0]}:"
        if op == "GOTO":
            return f"GOTO {args[0]}"
        if op == "IF_FALSE":
            return f"IF_FALSE {args[0]} GOTO {args[1]}"
        if op == "PRINT":
            return f"PRINT {args[0]}"
        if op == "ASSIGN":
            return f"{args[0]} = {args[1]}"
        if op == "UNARY":
            return f"{args[0]} = {args[1]}{args[2]}"
        if op == "BINARY":
            return f"{args[0]} = {args[1]} {args[2]} {args[3]}"
        return f"{op} {' '.join(map(str, args))}"


class CodeGenerator:
    def __init__(self):
        self.instructions = []
        self.temporary_count = 0
        self.label_count = 0
        self.loop_labels = []

    def generate(self, program):
        for statement in program.statements:
            self.visit(statement)
        return self.instructions

    def emit(self, operation, *arguments, line=0):
        self.instructions.append(Instruction(operation, arguments, line))

    def temporary(self):
        self.temporary_count += 1
        return f"t{self.temporary_count}"

    def label(self, prefix):
        self.label_count += 1
        return f"{prefix}_{self.label_count}"

    def visit(self, node):
        if isinstance(node, VariableDeclaration):
            self.emit("ASSIGN", node.name, self.expression(node.initializer), line=node.line)
        elif isinstance(node, Assignment):
            self.emit("ASSIGN", node.name, self.expression(node.value), line=node.line)
        elif isinstance(node, CompoundAssignment):
            right = self.expression(node.value)
            temp = self.temporary()
            self.emit("BINARY", temp, node.name, node.operator[0], right, line=node.line)
            self.emit("ASSIGN", node.name, temp, line=node.line)
        elif isinstance(node, PrintStatement):
            self.emit("PRINT", self.expression(node.expression), line=node.line)
        elif isinstance(node, IfStatement):
            condition = self.expression(node.condition)
            false_label = self.label("else")
            end_label = self.label("endif")
            self.emit("IF_FALSE", condition, false_label, line=node.line)
            for statement in node.then_branch:
                self.visit(statement)
            if node.else_branch is not None:
                self.emit("GOTO", end_label, line=node.line)
                self.emit("LABEL", false_label, line=node.line)
                for statement in node.else_branch:
                    self.visit(statement)
                self.emit("LABEL", end_label, line=node.line)
            else:
                self.emit("LABEL", false_label, line=node.line)
        elif isinstance(node, WhileStatement):
            start_label = self.label("while")
            end_label = self.label("endwhile")
            self.emit("LABEL", start_label, line=node.line)
            condition = self.expression(node.condition)
            self.emit("IF_FALSE", condition, end_label, line=node.line)
            self.loop_labels.append((start_label, end_label))
            for statement in node.body:
                self.visit(statement)
            self.loop_labels.pop()
            self.emit("GOTO", start_label, line=node.line)
            self.emit("LABEL", end_label, line=node.line)
        elif isinstance(node, BreakStatement):
            self.emit("GOTO", self.loop_labels[-1][1], line=node.line)
        elif isinstance(node, ContinueStatement):
            self.emit("GOTO", self.loop_labels[-1][0], line=node.line)

    def expression(self, node):
        if isinstance(node, Number):
            return Constant(node.value)
        if isinstance(node, String):
            return Constant(node.value)
        if isinstance(node, Boolean):
            return Constant(node.value)
        if isinstance(node, Identifier):
            return node.name
        if isinstance(node, UnaryExpression):
            operand = self.expression(node.operand)
            result = self.temporary()
            self.emit("UNARY", result, operand, node.operator, line=node.line)
            return result
        if isinstance(node, BinaryExpression):
            left = self.expression(node.left)
            right = self.expression(node.right)
            result = self.temporary()
            self.emit("BINARY", result, left, node.operator, right, line=node.line)
            return result
        raise TypeError(f"Unsupported AST expression: {type(node).__name__}")


def format_instructions(instructions):
    return "\n".join(f"{index + 1:02d}. {instruction}" for index, instruction in enumerate(instructions))
