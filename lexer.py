"""Phase 1: convert MiniLang source text into a token stream."""

from dataclasses import dataclass

from errors import LexerError


@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int

    def __str__(self):
        return f"{self.type}({self.value!r}) at {self.line}:{self.column}"


class Lexer:
    KEYWORDS = {"let", "print", "if", "else", "while", "break", "continue"}
    TWO_CHARACTER_OPERATORS = {">=", "<=", "==", "!=", "&&", "||", "+=", "-=", "*=", "/="}
    ONE_CHARACTER_TOKENS = {
        "+": "PLUS", "-": "MINUS", "*": "STAR", "/": "SLASH", "%": "PERCENT",
        ">": "GREATER", "<": "LESS", "=": "ASSIGN", "!": "BANG",
        "(": "LPAREN", ")": "RPAREN", "{": "LBRACE", "}": "RBRACE", ";": "SEMICOLON",
    }

    def tokenize(self, source):
        tokens = []
        index, line, column = 0, 1, 1
        while index < len(source):
            character = source[index]
            if character in " \t\r":
                index += 1
                column += 1
                continue
            if character == "\n":
                index += 1
                line += 1
                column = 1
                continue
            if source.startswith("//", index):
                while index < len(source) and source[index] != "\n":
                    index += 1
                    column += 1
                continue
            if character == '"':
                token, consumed = self.read_string(source, index, line, column)
                tokens.append(token)
                index += consumed
                column += consumed
                continue
            if character.isalpha() or character == "_":
                start_column = column
                start = index
                while index < len(source) and (source[index].isalnum() or source[index] == "_"):
                    index += 1
                    column += 1
                value = source[start:index]
                if value == "true":
                    token_type = "TRUE"
                elif value == "false":
                    token_type = "FALSE"
                else:
                    token_type = "KEYWORD" if value in self.KEYWORDS else "IDENTIFIER"
                tokens.append(Token(token_type, value, line, start_column))
                continue
            if character.isdigit():
                start_column = column
                start = index
                while index < len(source) and source[index].isdigit():
                    index += 1
                    column += 1
                token_type = "NUMBER"
                if index < len(source) and source[index] == ".":
                    token_type = "FLOAT"
                    index += 1
                    column += 1
                    if index >= len(source) or not source[index].isdigit():
                        raise LexerError("A floating-point literal needs digits after '.'.", line, column)
                    while index < len(source) and source[index].isdigit():
                        index += 1
                        column += 1
                tokens.append(Token(token_type, source[start:index], line, start_column))
                continue
            pair = source[index:index + 2]
            if pair in self.TWO_CHARACTER_OPERATORS:
                tokens.append(Token("OPERATOR", pair, line, column))
                index += 2
                column += 2
                continue
            if character in self.ONE_CHARACTER_TOKENS:
                tokens.append(Token(self.ONE_CHARACTER_TOKENS[character], character, line, column))
                index += 1
                column += 1
                continue
            raise LexerError(f"Invalid character {character!r}.", line, column, character)
        tokens.append(Token("EOF", "", line, column))
        return tokens

    def read_string(self, source, start, line, column):
        index = start + 1
        value = []
        while index < len(source) and source[index] != '"':
            if source[index] == "\n":
                raise LexerError("String literal cannot cross a line.", line, column)
            if source[index] == "\\" and index + 1 < len(source):
                escaped = source[index + 1]
                value.append({"n": "\n", "t": "\t", '"': '"', "\\": "\\"}.get(escaped, escaped))
                index += 2
            else:
                value.append(source[index])
                index += 1
        if index >= len(source):
            raise LexerError("Unterminated string literal.", line, column)
        return Token("STRING", "".join(value), line, column), index + 1 - start
