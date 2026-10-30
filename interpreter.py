"""Phase 5: execute typed intermediate instructions safely."""

from code_generator import Constant
from errors import ExecutionError


class Interpreter:
    MAX_STEPS = 100_000

    def execute(self, instructions, max_steps=MAX_STEPS):
        values = {}
        labels = {instruction.arguments[0]: index for index, instruction in enumerate(instructions) if instruction.operation == "LABEL"}
        output = []
        program_counter = 0
        steps = 0
        while program_counter < len(instructions):
            steps += 1
            if steps > max_steps:
                raise ExecutionError(f"Execution limit of {max_steps} instructions exceeded; possible infinite loop.")
            instruction = instructions[program_counter]
            operation = instruction.operation
            arguments = instruction.arguments
            if operation == "LABEL":
                program_counter += 1
                continue
            if operation == "ASSIGN":
                values[arguments[0]] = self.value_of(arguments[1], values, instruction)
            elif operation == "UNARY":
                operand = self.value_of(arguments[1], values, instruction)
                if arguments[2] == "-":
                    values[arguments[0]] = -operand
                elif arguments[2] == "!":
                    values[arguments[0]] = not operand
            elif operation == "BINARY":
                left = self.value_of(arguments[1], values, instruction)
                right = self.value_of(arguments[3], values, instruction)
                values[arguments[0]] = self.calculate(left, arguments[2], right, instruction)
            elif operation == "PRINT":
                output.append(self.format_value(self.value_of(arguments[0], values, instruction)))
            elif operation == "GOTO":
                program_counter = self.jump_to(labels, arguments[0], instruction)
                continue
            elif operation == "IF_FALSE":
                if not self.value_of(arguments[0], values, instruction):
                    program_counter = self.jump_to(labels, arguments[1], instruction)
                    continue
            program_counter += 1
        return output, values

    def value_of(self, operand, values, instruction):
        if isinstance(operand, Constant):
            return operand.value
        if operand in values:
            return values[operand]
        raise ExecutionError(f"Unknown value '{operand}'.", instruction.line)

    def calculate(self, left, operator, right, instruction):
        if operator == "/":
            if right == 0:
                raise ExecutionError("Division by zero.", instruction.line)
            return left / right
        if operator == "%":
            if right == 0:
                raise ExecutionError("Modulo by zero.", instruction.line)
            return left % right
        if operator == "+":
            return left + right
        if operator == "-":
            return left - right
        if operator == "*":
            return left * right
        if operator == ">":
            return left > right
        if operator == "<":
            return left < right
        if operator == ">=":
            return left >= right
        if operator == "<=":
            return left <= right
        if operator == "==":
            return left == right
        if operator == "!=":
            return left != right
        if operator == "&&":
            return left and right
        if operator == "||":
            return left or right
        raise ExecutionError(f"Unsupported operator '{operator}'.", instruction.line)

    def jump_to(self, labels, label, instruction):
        if label not in labels:
            raise ExecutionError(f"Unknown label '{label}'.", instruction.line)
        return labels[label]

    @staticmethod
    def format_value(value):
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)
