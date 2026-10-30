import unittest

from code_generator import CodeGenerator
from errors import ExecutionError, LexerError, SemanticError, SyntaxCompilerError
from interpreter import Interpreter
from lexer import Lexer
from machine_code import MachineCodeGenerator, VirtualMachine
from optimizer import Optimizer
from parser import Parser
from semantic import SemanticAnalyzer


def compile_pipeline(source):
    tree = Parser(Lexer().tokenize(source)).parse()
    SemanticAnalyzer().analyze(tree)
    original = CodeGenerator().generate(tree)
    optimized = Optimizer().optimize(original)
    machine = MachineCodeGenerator().generate(optimized.instructions)
    return original, optimized, machine


def run(source):
    _, _, machine = compile_pipeline(source)
    return VirtualMachine().execute(machine)[0]


class MiniCompilerTests(unittest.TestCase):
    def test_integer_variables(self):
        self.assertEqual(run("let x = 7; print(x);"), ["7"])

    def test_float_variables(self):
        self.assertEqual(run("let price = 99.50; print(price);"), ["99.5"])

    def test_boolean_variables(self):
        self.assertEqual(run("let active = true; print(active);"), ["true"])

    def test_string_variables(self):
        self.assertEqual(run('let name = "MiniLang"; print(name);'), ["MiniLang"])

    def test_arithmetic_and_modulo(self):
        self.assertEqual(run("let x = 10 + 20 * 2; let y = 10 % 3; print(x); print(y);"), ["50", "1"])

    def test_precedence_and_parentheses(self):
        self.assertEqual(run("let x = (10 + 20) * 2; print(x);"), ["60"])

    def test_comparisons(self):
        self.assertEqual(run("print(10 > 5); print(10 < 20); print(10 == 10); print(10 != 5);"), ["true", "true", "true", "true"])

    def test_logical_operators(self):
        self.assertEqual(run("print(true && false); print(true || false); print(!false);"), ["false", "true", "true"])

    def test_if_statement(self):
        self.assertEqual(run("let x = 5; if (x > 2) { print(x); }"), ["5"])

    def test_if_else_statement(self):
        self.assertEqual(run("let x = 1; if (x > 2) { print(5); } else { print(0); }"), ["0"])

    def test_while_loop(self):
        self.assertEqual(run("let x = 0; while (x < 3) { x = x + 1; } print(x);"), ["3"])

    def test_break_and_continue(self):
        source = "let x = 0; while (x < 5) { x += 1; if (x == 2) { continue; } if (x == 4) { break; } print(x); }"
        self.assertEqual(run(source), ["1", "3"])

    def test_comments(self):
        self.assertEqual(run("// ignored\nlet x = 10; // also ignored\nprint(x);"), ["10"])

    def test_assignments(self):
        self.assertEqual(run("let x = 2; x *= 4; x -= 1; print(x);"), ["7"])

    def test_type_mismatch(self):
        with self.assertRaisesRegex(SemanticError, "Invalid operand types"):
            run('let x = "a" + 1;')

    def test_undeclared_variable(self):
        with self.assertRaisesRegex(SemanticError, "Variable 'x' is not declared"):
            run("print(x);")

    def test_condition_must_be_boolean(self):
        with self.assertRaisesRegex(SemanticError, "Condition must be Boolean"):
            run("if (10) { print(1); }")

    def test_break_outside_loop(self):
        with self.assertRaisesRegex(SemanticError, "break.*while"):
            run("break;")

    def test_invalid_syntax(self):
        with self.assertRaises(SyntaxCompilerError):
            run("let x = ;")

    def test_missing_semicolon_and_columns(self):
        with self.assertRaisesRegex(SyntaxCompilerError, "column"):
            run("let x = 10")

    def test_invalid_character(self):
        with self.assertRaisesRegex(LexerError, "Invalid character.*column"):
            run("let x = 10 @ 2;")

    def test_division_by_zero(self):
        with self.assertRaisesRegex(ExecutionError, "Division by zero"):
            run("let x = 10 / 0; print(x);")

    def test_infinite_loop_limit(self):
        source = "let x = 0; while (true) { x = x + 1; }"
        _, _, machine = compile_pipeline(source)
        with self.assertRaisesRegex(ExecutionError, "execution limit"):
            VirtualMachine().execute(machine, max_steps=50)

    def test_constant_folding(self):
        _, optimized, _ = compile_pipeline("let x = 10 + 20; print(x);")
        self.assertIn("Constant folding", optimized.applied)
        self.assertTrue(any("x = 30" in str(item) for item in optimized.instructions))

    def test_constant_propagation(self):
        _, optimized, _ = compile_pipeline("let x = 10; let y = x + 5; print(y);")
        self.assertTrue(any("y = 15" in str(item) for item in optimized.instructions))

    def test_algebraic_simplification(self):
        _, optimized, _ = compile_pipeline("let x = 10; let y = x * 1; print(y);")
        self.assertIn("Algebraic simplification", optimized.applied)

    def test_machine_code_generation(self):
        original, _, _ = compile_pipeline("let a = 10; let b = 20; print(a + b);")
        machine = MachineCodeGenerator().generate(original)
        operations = [item.operation for item in machine]
        self.assertIn("LOAD_CONST", operations)
        self.assertIn("ADD", operations)
        self.assertIn("PRINT", operations)
        self.assertEqual(operations[-1], "HALT")

    def test_machine_code_execution(self):
        self.assertEqual(run("let a = 10; let b = 20; print(a + b);"), ["30"])


if __name__ == "__main__":
    unittest.main()
