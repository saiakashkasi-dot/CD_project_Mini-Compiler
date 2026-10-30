# Design and Development of a Mini Compiler for a Sample Programming Language

MiniCompiler is a beginner-friendly Python 3 college project implementing a small programming language named **MiniLang**. It demonstrates a complete educational compiler pipeline:

```text
MiniLang Source
      |
      v
Lexer -> Tokens -> Recursive-descent Parser -> AST
                                      |
                                      v
                              Semantic Analyzer
                                      |
                                      v
                              Symbol Table + IR
                                      |
                                      v
                                  Optimizer
                                      |
                                      v
                         Educational Machine Code
                                      |
                                      v
                              Virtual Machine
                                      |
                                      v
                                   Output
```

## Objectives

- Demonstrate lexical analysis, syntax analysis, semantic analysis, IR generation, optimization, target-code generation, and execution.
- Keep every phase separate and readable for a college compiler-design viva.
- Provide useful source line and column diagnostics.
- Show the difference between original IR, optimized IR, and educational machine code.

## MiniLang Features

### Data types

- Integer: `10`
- Float: `99.50`
- Boolean: `true`, `false`
- String: `"MiniLang"`

Declarations use type inference from the initializer:

```text
let age = 20;
let price = 99.50;
let name = "MiniLang";
let active = true;
```

MiniLang does not perform implicit conversions between unrelated types. Integer and float arithmetic can be mixed and produces a float when needed. Strings support concatenation with `+`. Boolean values support logical operations.

### Operators and precedence

From low to high precedence:

```text
||
&&
== !=
> < >= <=
+ -
* / %
unary - !
parentheses
```

Supported operators include arithmetic, comparisons, logical `&&`, `||`, `!`, modulo `%`, and compound assignment `+=`, `-=`, `*=`, `/=`.

### Statements

```text
let x = 0;
x = x + 1;
x += 5;
print(x);

if (x > 5) {
    print("large");
} else {
    print("small");
}

while (x < 10) {
    x += 1;
    if (x == 8) {
        continue;
    }
    if (x == 9) {
        break;
    }
}
```

Single-line comments begin with `//` and are ignored by the lexer. Blocks can be nested.

## Compiler Phases

1. **Lexical analysis** (`lexer.py`): recognizes keywords, identifiers, integers, floats, strings, booleans, operators, punctuation, and comments.
2. **Syntax analysis** (`parser.py`): recursive descent with separate precedence levels builds the AST.
3. **Semantic analysis** (`semantic.py`, `symbol_table.py`): checks declaration order, operand types, assignment types, boolean conditions, and loop-only `break`/`continue`.
4. **Intermediate representation** (`code_generator.py`): produces typed three-address-style instructions, labels, jumps, temporaries, and `PRINT` operations.
5. **Optimization** (`optimizer.py`): performs safe constant folding, constant propagation, algebraic simplification, and conservative dead-code elimination.
6. **Machine code generation** (`machine_code.py`): translates IR to a small assembly-like educational instruction set.
7. **Virtual machine** (`machine_code.py`): executes that target instruction set and returns program output.

## Educational Machine Code

The machine-code stage is **not native x86 or ARM code**. It is a documented educational target ISA executed by `VirtualMachine`:

| Instruction | Meaning |
|---|---|
| `LOAD_CONST value` | Push a literal value |
| `LOAD name` | Push a variable from memory |
| `STORE name` | Pop and store in memory |
| `ADD`, `SUB`, `MUL`, `DIV`, `MOD` | Numeric or string operations where valid |
| `CMP_GT`, `CMP_LT`, `CMP_GE`, `CMP_LE`, `CMP_EQ`, `CMP_NE` | Comparisons |
| `AND`, `OR`, `NOT`, `NEG` | Logical and unary operations |
| `JMP label` | Unconditional jump |
| `JMP_IF_FALSE label` | Pop condition and jump when false |
| `LABEL label` | Control-flow target |
| `PRINT` | Pop and append to output |
| `HALT` | Stop the virtual machine |

Example source:

```text
let a = 10;
let b = 20;
let result = a + b;
print(result);
```

Possible unoptimized target code:

```text
LOAD_CONST 10
STORE a
LOAD_CONST 20
STORE b
LOAD a
LOAD b
ADD
STORE t1
LOAD t1
STORE result
LOAD result
PRINT
HALT
```

Optimization may replace this with a shorter constant form. The GUI shows both original and optimized IR, followed by machine code generated from optimized IR.

## Error Handling

Errors are custom exceptions with phase, line, column, and token context where available:

```text
Lexical Error: Invalid character '@' at line 2, column 5 near '@'
Syntax Error: Expected ';' after variable declaration at line 3, column 15 near 'EOF'
Semantic Error: Variable 'total' is not declared at line 7, column 11 near 'total'
Runtime Error: Division by zero at line 8
```

The GUI remains open after invalid input and reports the failed phase in its status line.

## GUI

Run `python main.py` to open the Tkinter compiler laboratory. It contains:

- MiniLang source editor
- Compile and Clear buttons
- Tokens
- Syntax / AST
- Semantic Analysis and symbol types
- Original Intermediate Code
- Optimization summary and applied transformations
- Optimized Intermediate Code
- Educational Machine Code
- Program Output
- Compilation status

## Project Structure

```text
MiniCompiler/
├── main.py                 # Tkinter entrypoint
├── gui.py                  # Complete compiler laboratory GUI
├── lexer.py                # Phase 1: tokenizer
├── parser.py               # Phase 2: recursive-descent parser
├── ast_nodes.py            # AST dataclasses
├── semantic.py             # Phase 3: type and name checks
├── symbol_table.py         # Typed symbol table
├── code_generator.py       # Phase 4: three-address IR
├── optimizer.py            # Constant and algebraic optimizations
├── machine_code.py         # Educational ISA generator and VM
├── interpreter.py          # Direct IR executor and loop safety
├── errors.py               # Phase-aware compiler errors
├── requirements.txt        # No external packages
├── tests/
│   └── test_compiler.py    # 28 feature and integration tests
└── examples/
    ├── basic.min
    ├── data_types.min
    ├── arithmetic.min
    ├── if_else.min
    ├── while.min
    ├── logical.min
    ├── strings.min
    ├── optimization.min
    ├── machine_code.min
    ├── comments.min
    └── errors/
        ├── lexical_error.min
        ├── syntax_error.min
        ├── semantic_error.min
        └── runtime_error.min
```

## Installation and Running

Python 3.10 or newer is recommended. The project uses only Python standard-library modules, so no package installation is required.

From the `MiniCompiler` directory:

```bash
python main.py
```

## Testing

Run all tests:

```bash
python -m unittest discover -s tests -v
```

The suite covers integers, floats, booleans, strings, arithmetic, precedence, parentheses, comparisons, logical operators, if/else, while, break, continue, comments, modulo, assignments, semantic/syntax/lexical/runtime errors, loop limits, optimization, machine-code generation, and machine-code execution.

## Complete Example

```text
// typed values, logic, loop, modulo, and string output
let count = 0;
let active = true;
let label = "value: ";

while (count < 5 && active) {
    if (count % 2 == 0) {
        print(label + "even");
    } else {
        print(label + "odd");
    }
    count += 1;
}
```

Expected output:

```text
value: even
value: odd
value: even
value: odd
value: even
```

## Limitations and Future Enhancements

This educational language currently has no user-defined functions, arrays, file I/O, or lexical block scopes. Possible future work includes functions and return values, arrays, richer static types, syntax highlighting, source-level debugging, and a bytecode serializer.
