"""Abstract Syntax Tree node definitions for MiniLang."""

from dataclasses import dataclass, field
from typing import List, Optional


class ASTNode:
    line: int = 0
    column: int = 0


@dataclass
class Program(ASTNode):
    statements: List[ASTNode] = field(default_factory=list)


@dataclass
class Number(ASTNode):
    value: int | float
    line: int = 0
    column: int = 0


@dataclass
class String(ASTNode):
    value: str
    line: int = 0
    column: int = 0


@dataclass
class Boolean(ASTNode):
    value: bool
    line: int = 0
    column: int = 0


@dataclass
class Identifier(ASTNode):
    name: str
    line: int = 0
    column: int = 0


@dataclass
class BinaryExpression(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode
    line: int = 0
    column: int = 0


@dataclass
class UnaryExpression(ASTNode):
    operator: str
    operand: ASTNode
    line: int = 0
    column: int = 0


@dataclass
class VariableDeclaration(ASTNode):
    name: str
    initializer: ASTNode
    line: int = 0
    column: int = 0


@dataclass
class Assignment(ASTNode):
    name: str
    value: ASTNode
    line: int = 0
    column: int = 0


@dataclass
class CompoundAssignment(ASTNode):
    name: str
    operator: str
    value: ASTNode
    line: int = 0
    column: int = 0


@dataclass
class PrintStatement(ASTNode):
    expression: ASTNode
    line: int = 0
    column: int = 0


@dataclass
class IfStatement(ASTNode):
    condition: ASTNode
    then_branch: List[ASTNode]
    else_branch: Optional[List[ASTNode]] = None
    line: int = 0
    column: int = 0


@dataclass
class WhileStatement(ASTNode):
    condition: ASTNode
    body: List[ASTNode]
    line: int = 0
    column: int = 0


@dataclass
class BreakStatement(ASTNode):
    line: int = 0
    column: int = 0


@dataclass
class ContinueStatement(ASTNode):
    line: int = 0
    column: int = 0
