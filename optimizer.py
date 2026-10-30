"""Educational, conservative optimization pass for MiniLang IR."""

from dataclasses import dataclass, field

from code_generator import Constant, Instruction


@dataclass
class OptimizationResult:
    instructions: list
    applied: list = field(default_factory=list)
    original_count: int = 0


class Optimizer:
    def optimize(self, instructions):
        result = []
        constants = {}
        applied = []
        original_used = self.used_names(instructions)
        for instruction in instructions:
            if instruction.operation in ("LABEL", "GOTO", "IF_FALSE"):
                constants.clear()
                result.append(instruction)
                continue
            if instruction.operation == "ASSIGN":
                target, operand = instruction.arguments
                operand = self.replace_constant(operand, constants)
                result.append(Instruction("ASSIGN", (target, operand), instruction.line))
                if isinstance(operand, Constant):
                    constants[target] = operand
                else:
                    constants.pop(target, None)
                continue
            if instruction.operation == "BINARY":
                target, left, operator, right = instruction.arguments
                algebraic_candidate = isinstance(right, Constant) and ((operator in ("+", "-") and right.value == 0) or (operator in ("*", "/") and right.value == 1))
                left = self.replace_constant(left, constants)
                right = self.replace_constant(right, constants)
                simplified = self.simplify(left, operator, right)
                if simplified is not None:
                    result.append(Instruction("ASSIGN", (target, simplified), instruction.line))
                    constants[target] = simplified
                    if algebraic_candidate:
                        applied.append("Algebraic simplification")
                    elif isinstance(left, Constant) and isinstance(right, Constant):
                        applied.append("Constant folding")
                    else:
                        applied.append("Algebraic simplification")
                else:
                    result.append(Instruction("BINARY", (target, left, operator, right), instruction.line))
                    constants.pop(target, None)
                continue
            if instruction.operation == "UNARY":
                target, operand, operator = instruction.arguments
                operand = self.replace_constant(operand, constants)
                if isinstance(operand, Constant):
                    value = not operand.value if operator == "!" else -operand.value
                    constant = Constant(value)
                    result.append(Instruction("ASSIGN", (target, constant), instruction.line))
                    constants[target] = constant
                    applied.append("Constant folding")
                else:
                    result.append(Instruction("UNARY", (target, operand, operator), instruction.line))
                    constants.pop(target, None)
                continue
            if instruction.operation == "PRINT":
                result.append(Instruction("PRINT", (self.replace_constant(instruction.arguments[0], constants),), instruction.line))
                continue
            result.append(instruction)
        result, removed = self.remove_unused_assignments(result, original_used)
        if removed:
            applied.append("Dead code elimination")
        return OptimizationResult(result, sorted(set(applied)), len(instructions))

    @staticmethod
    def replace_constant(operand, constants):
        return constants.get(operand, operand) if isinstance(operand, str) else operand

    @staticmethod
    def simplify(left, operator, right):
        if isinstance(left, Constant) and isinstance(right, Constant):
            if operator == "/" and right.value == 0 or operator == "%" and right.value == 0:
                return None
            try:
                if operator == "+":
                    return Constant(left.value + right.value)
                if operator == "-":
                    return Constant(left.value - right.value)
                if operator == "*":
                    return Constant(left.value * right.value)
                if operator == "/":
                    return Constant(left.value / right.value)
                if operator == "%":
                    return Constant(left.value % right.value)
                if operator == ">":
                    return Constant(left.value > right.value)
                if operator == "<":
                    return Constant(left.value < right.value)
                if operator == ">=":
                    return Constant(left.value >= right.value)
                if operator == "<=":
                    return Constant(left.value <= right.value)
                if operator == "==":
                    return Constant(left.value == right.value)
                if operator == "!=":
                    return Constant(left.value != right.value)
                if operator == "&&":
                    return Constant(left.value and right.value)
                if operator == "||":
                    return Constant(left.value or right.value)
            except (TypeError, ZeroDivisionError):
                return None
        if isinstance(right, Constant):
            if operator == "+" and right.value == 0 or operator == "-" and right.value == 0:
                return left if isinstance(left, Constant) else left
            if operator == "*" and right.value == 1 or operator == "/" and right.value == 1:
                return left if isinstance(left, Constant) else left
        return None

    @staticmethod
    def remove_unused_assignments(instructions, original_used):
        used = set()
        for instruction in instructions:
            if instruction.operation in ("BINARY", "UNARY"):
                used.update(value for value in (instruction.arguments[1], instruction.arguments[-1]) if isinstance(value, str))
            elif instruction.operation in ("PRINT", "IF_FALSE"):
                used.update(value for value in instruction.arguments if isinstance(value, str))
        filtered = []
        removed = False
        for instruction in instructions:
            if instruction.operation == "ASSIGN" and instruction.arguments[0] not in used and instruction.arguments[0] not in original_used:
                removed = True
                continue
            filtered.append(instruction)
        return filtered, removed

    @staticmethod
    def used_names(instructions):
        names = set()
        for instruction in instructions:
            if instruction.operation == "BINARY":
                names.update(value for value in (instruction.arguments[1], instruction.arguments[3]) if isinstance(value, str))
            elif instruction.operation == "UNARY":
                if isinstance(instruction.arguments[1], str):
                    names.add(instruction.arguments[1])
            elif instruction.operation in ("PRINT", "IF_FALSE"):
                names.update(value for value in instruction.arguments if isinstance(value, str))
        return names
