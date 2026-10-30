"""Educational assembly-like target and virtual machine.

This is not native x86 or ARM code. It is a small documented target ISA that
makes the final compiler phase visible and executable for learning.
"""

from dataclasses import dataclass

from code_generator import Constant
from errors import ExecutionError


@dataclass
class MachineInstruction:
    operation: str
    argument: object = None
    line: int = 0

    def __str__(self):
        return f"{self.operation} {self.argument}" if self.argument is not None else self.operation


class MachineCodeGenerator:
    OPERATOR_INSTRUCTIONS = {
        "+": "ADD", "-": "SUB", "*": "MUL", "/": "DIV", "%": "MOD",
        ">": "CMP_GT", "<": "CMP_LT", ">=": "CMP_GE", "<=": "CMP_LE",
        "==": "CMP_EQ", "!=": "CMP_NE", "&&": "AND", "||": "OR",
    }

    def generate(self, instructions):
        machine = []
        for instruction in instructions:
            operation = instruction.operation
            args = instruction.arguments
            if operation == "LABEL":
                machine.append(MachineInstruction("LABEL", args[0], instruction.line))
            elif operation == "ASSIGN":
                self.load(machine, args[1], instruction.line)
                machine.append(MachineInstruction("STORE", args[0], instruction.line))
            elif operation == "BINARY":
                self.load(machine, args[1], instruction.line)
                self.load(machine, args[3], instruction.line)
                machine.append(MachineInstruction(self.OPERATOR_INSTRUCTIONS[args[2]], line=instruction.line))
                machine.append(MachineInstruction("STORE", args[0], instruction.line))
            elif operation == "UNARY":
                self.load(machine, args[1], instruction.line)
                machine.append(MachineInstruction("NOT" if args[2] == "!" else "NEG", line=instruction.line))
                machine.append(MachineInstruction("STORE", args[0], instruction.line))
            elif operation == "PRINT":
                self.load(machine, args[0], instruction.line)
                machine.append(MachineInstruction("PRINT", line=instruction.line))
            elif operation == "GOTO":
                machine.append(MachineInstruction("JMP", args[0], instruction.line))
            elif operation == "IF_FALSE":
                self.load(machine, args[0], instruction.line)
                machine.append(MachineInstruction("JMP_IF_FALSE", args[1], instruction.line))
        machine.append(MachineInstruction("HALT"))
        return machine

    @staticmethod
    def load(machine, operand, line):
        if isinstance(operand, Constant):
            machine.append(MachineInstruction("LOAD_CONST", operand.value, line))
        else:
            machine.append(MachineInstruction("LOAD", operand, line))


def format_machine_code(instructions):
    return "\n".join(f"{index + 1:02d}. {instruction}" for index, instruction in enumerate(instructions))


class VirtualMachine:
    MAX_STEPS = 100_000

    def execute(self, instructions, max_steps=MAX_STEPS):
        labels = {instruction.argument: index for index, instruction in enumerate(instructions) if instruction.operation == "LABEL"}
        stack = []
        memory = {}
        output = []
        program_counter = 0
        steps = 0
        while program_counter < len(instructions):
            steps += 1
            if steps > max_steps:
                raise ExecutionError(f"Machine execution limit of {max_steps} instructions exceeded; possible infinite loop.")
            instruction = instructions[program_counter]
            op = instruction.operation
            arg = instruction.argument
            if op == "HALT":
                break
            if op == "LABEL":
                program_counter += 1
                continue
            if op == "LOAD_CONST":
                stack.append(arg)
            elif op == "LOAD":
                if arg not in memory:
                    raise ExecutionError(f"Unknown variable '{arg}'.", instruction.line)
                stack.append(memory[arg])
            elif op == "STORE":
                memory[arg] = stack.pop()
            elif op == "PRINT":
                output.append(self.format_value(stack.pop()))
            elif op == "JMP":
                program_counter = self.jump(labels, arg, instruction)
                continue
            elif op == "JMP_IF_FALSE":
                if not stack.pop():
                    program_counter = self.jump(labels, arg, instruction)
                    continue
            else:
                self.apply_operator(op, stack, instruction)
            program_counter += 1
        return output, memory

    def apply_operator(self, operation, stack, instruction):
        if operation in ("NEG", "NOT"):
            value = stack.pop()
            stack.append(-value if operation == "NEG" else not value)
            return
        right = stack.pop()
        left = stack.pop()
        if operation == "DIV":
            if right == 0:
                raise ExecutionError("Division by zero.", instruction.line)
            value = left / right
        elif operation == "MOD":
            if right == 0:
                raise ExecutionError("Modulo by zero.", instruction.line)
            value = left % right
        else:
            value = {
                "ADD": lambda: left + right, "SUB": lambda: left - right,
                "MUL": lambda: left * right, "CMP_GT": lambda: left > right,
                "CMP_LT": lambda: left < right, "CMP_GE": lambda: left >= right,
                "CMP_LE": lambda: left <= right, "CMP_EQ": lambda: left == right,
                "CMP_NE": lambda: left != right, "AND": lambda: left and right,
                "OR": lambda: left or right,
            }.get(operation, lambda: None)()
        if value is None:
            raise ExecutionError(f"Unknown machine instruction '{operation}'.", instruction.line)
        stack.append(value)

    @staticmethod
    def jump(labels, label, instruction):
        if label not in labels:
            raise ExecutionError(f"Unknown label '{label}'.", instruction.line)
        return labels[label]

    @staticmethod
    def format_value(value):
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)
