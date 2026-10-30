"""Phase 3: name resolution and beginner-friendly static type checking."""

from ast_nodes import (Assignment, BinaryExpression, Boolean, BreakStatement,
                       CompoundAssignment, ContinueStatement, Identifier,
                       IfStatement, Number, PrintStatement, Program, String,
                       UnaryExpression, VariableDeclaration, WhileStatement)
from errors import SemanticError
from symbol_table import SymbolTable


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.loop_depth = 0

    def analyze(self, program):
        self.visit(program)
        return self.symbol_table

    def visit(self, node):
        if isinstance(node, Program):
            for statement in node.statements:
                self.visit(statement)
        elif isinstance(node, VariableDeclaration):
            if self.symbol_table.contains(node.name):
                raise SemanticError(f"Variable '{node.name}' is already declared.", node.line, node.column)
            type_name = self.expression_type(node.initializer)
            self.symbol_table.declare(node.name, type_name, node.line, node.column)
        elif isinstance(node, Assignment):
            symbol = self.require_declared(node.name, node.line, node.column)
            value_type = self.expression_type(node.value)
            self.require_same_type(symbol.type_name, value_type, node.line, node.column, f"Cannot assign {value_type} to {symbol.type_name} variable '{node.name}'.")
        elif isinstance(node, CompoundAssignment):
            symbol = self.require_declared(node.name, node.line, node.column)
            value_type = self.expression_type(node.value)
            result_type = self.binary_type(symbol.type_name, node.operator[0], value_type, node.line, node.column)
            self.require_same_type(symbol.type_name, result_type, node.line, node.column, f"Compound assignment would change '{node.name}' from {symbol.type_name} to {result_type}.")
        elif isinstance(node, PrintStatement):
            self.expression_type(node.expression)
        elif isinstance(node, IfStatement):
            self.require_boolean(self.expression_type(node.condition), node.line, node.column)
            for statement in node.then_branch:
                self.visit(statement)
            if node.else_branch:
                for statement in node.else_branch:
                    self.visit(statement)
        elif isinstance(node, WhileStatement):
            self.require_boolean(self.expression_type(node.condition), node.line, node.column)
            self.loop_depth += 1
            for statement in node.body:
                self.visit(statement)
            self.loop_depth -= 1
        elif isinstance(node, (BreakStatement, ContinueStatement)):
            if self.loop_depth == 0:
                raise SemanticError(f"'{type(node).__name__.replace('Statement', '').lower()}' can only be used inside a while loop.", node.line, node.column)

    def expression_type(self, node):
        if isinstance(node, Number):
            return "Float" if isinstance(node.value, float) else "Integer"
        if isinstance(node, String):
            return "String"
        if isinstance(node, Boolean):
            return "Boolean"
        if isinstance(node, Identifier):
            return self.require_declared(node.name, node.line, node.column).type_name
        if isinstance(node, UnaryExpression):
            operand_type = self.expression_type(node.operand)
            if node.operator == "-":
                if operand_type not in ("Integer", "Float"):
                    raise SemanticError(f"Invalid operand type {operand_type} for unary '-'.", node.line, node.column)
                return operand_type
            self.require_boolean(operand_type, node.line, node.column)
            return "Boolean"
        if isinstance(node, BinaryExpression):
            left_type = self.expression_type(node.left)
            right_type = self.expression_type(node.right)
            return self.binary_type(left_type, node.operator, right_type, node.line, node.column)
        raise SemanticError(f"Unsupported expression {type(node).__name__}.", getattr(node, "line", None), getattr(node, "column", None))

    def binary_type(self, left_type, operator, right_type, line, column):
        numeric = {"Integer", "Float"}
        if operator == "+" and left_type == right_type == "String":
            return "String"
        if operator in ("+", "-", "*", "/", "%") and left_type in numeric and right_type in numeric:
            return "Float" if "Float" in (left_type, right_type) or operator == "/" else "Integer"
        if operator in (">", "<", ">=", "<=") and left_type in numeric and right_type in numeric:
            return "Boolean"
        if operator in ("==", "!=") and left_type == right_type:
            return "Boolean"
        if operator in ("&&", "||") and left_type == right_type == "Boolean":
            return "Boolean"
        raise SemanticError(f"Invalid operand types for operator '{operator}': {left_type} and {right_type}.", line, column)

    def require_declared(self, name, line, column):
        symbol = self.symbol_table.lookup(name)
        if symbol is None:
            raise SemanticError(f"Variable '{name}' is not declared.", line, column, name)
        return symbol

    def require_boolean(self, type_name, line, column):
        if type_name != "Boolean":
            raise SemanticError(f"Condition must be Boolean, not {type_name}.", line, column)

    def require_same_type(self, expected, actual, line, column, message):
        if expected != actual:
            raise SemanticError(message, line, column)
