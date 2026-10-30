"""Symbol table entries used by semantic analysis."""

from dataclasses import dataclass


@dataclass
class Symbol:
    name: str
    type_name: str
    line: int
    column: int = 0


class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def declare(self, name, type_name, line, column=0):
        self.symbols[name] = Symbol(name, type_name, line, column)

    def contains(self, name):
        return name in self.symbols

    def lookup(self, name):
        return self.symbols.get(name)

    def names(self):
        return list(self.symbols)

    def types(self):
        return {name: symbol.type_name for name, symbol in self.symbols.items()}
