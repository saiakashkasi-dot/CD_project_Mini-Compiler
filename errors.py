"""Friendly, location-aware errors shared by every compiler phase."""


class CompilerError(Exception):
    phase = "Compiler"

    def __init__(self, message, line=None, column=None, token=None):
        self.message = message
        self.line = line
        self.column = column
        self.token = token
        location = ""
        if line is not None:
            location = f" at line {line}"
            if column is not None:
                location += f", column {column}"
        detail = f" near {token!r}" if token else ""
        super().__init__(f"{self.phase} Error: {message}{location}{detail}")


class LexerError(CompilerError):
    phase = "Lexical"


class ParserError(CompilerError):
    phase = "Syntax"


class SyntaxCompilerError(ParserError):
    """Backward-compatible name used by the original project."""


class SemanticError(CompilerError):
    phase = "Semantic"


class RuntimeCompilerError(CompilerError):
    phase = "Runtime"


RuntimeError = RuntimeCompilerError


class ExecutionError(RuntimeCompilerError):
    """Backward-compatible name used by the original project."""
