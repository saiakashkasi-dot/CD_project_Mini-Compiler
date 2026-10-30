"""Phase 2: recursive-descent parser with explicit precedence levels."""

from ast_nodes import (Assignment, BinaryExpression, Boolean, BreakStatement,
                       CompoundAssignment, ContinueStatement, Identifier,
                       IfStatement, Number, PrintStatement, Program, String,
                       UnaryExpression, VariableDeclaration, WhileStatement)
from errors import SyntaxCompilerError


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current(self):
        return self.tokens[self.position]

    def advance(self):
        token = self.current()
        self.position += 1
        return token

    def match(self, token_type, value=None):
        token = self.current()
        if token.type == token_type and (value is None or token.value == value):
            self.position += 1
            return token
        return None

    def expect(self, token_type, message, value=None):
        token = self.match(token_type, value)
        if token is None:
            current = self.current()
            raise SyntaxCompilerError(message, current.line, current.column, current.value or current.type)
        return token

    def parse(self):
        statements = []
        while self.current().type != "EOF":
            statements.append(self.parse_statement())
        return Program(statements)

    def parse_statement(self):
        token = self.current()
        if token.type == "KEYWORD" and token.value == "let":
            return self.parse_declaration()
        if token.type == "KEYWORD" and token.value == "print":
            return self.parse_print()
        if token.type == "KEYWORD" and token.value == "if":
            return self.parse_if()
        if token.type == "KEYWORD" and token.value == "while":
            return self.parse_while()
        if token.type == "KEYWORD" and token.value == "break":
            self.advance()
            self.expect("SEMICOLON", "Expected ';' after break.")
            return BreakStatement(token.line, token.column)
        if token.type == "KEYWORD" and token.value == "continue":
            self.advance()
            self.expect("SEMICOLON", "Expected ';' after continue.")
            return ContinueStatement(token.line, token.column)
        if token.type == "IDENTIFIER":
            return self.parse_assignment()
        raise SyntaxCompilerError("Expected a statement (let, assignment, print, if, while, break, or continue).", token.line, token.column, token.value or token.type)

    def parse_declaration(self):
        keyword = self.advance()
        name = self.expect("IDENTIFIER", "Expected a variable name after 'let'.")
        self.expect("ASSIGN", "Expected '=' after variable name.")
        initializer = self.parse_expression()
        self.expect("SEMICOLON", "Expected ';' after variable declaration.")
        return VariableDeclaration(name.value, initializer, keyword.line, name.column)

    def parse_assignment(self):
        name = self.advance()
        operator = self.current()
        if operator.type == "ASSIGN":
            self.advance()
            value = self.parse_expression()
            self.expect("SEMICOLON", "Expected ';' after assignment.")
            return Assignment(name.value, value, name.line, name.column)
        if operator.type == "OPERATOR" and operator.value in ("+=", "-=", "*=", "/="):
            self.advance()
            value = self.parse_expression()
            self.expect("SEMICOLON", "Expected ';' after compound assignment.")
            return CompoundAssignment(name.value, operator.value, value, name.line, name.column)
        raise SyntaxCompilerError("Expected '=' or a compound assignment operator after variable name.", operator.line, operator.column, operator.value)

    def parse_print(self):
        keyword = self.advance()
        self.expect("LPAREN", "Expected '(' after 'print'.")
        expression = self.parse_expression()
        self.expect("RPAREN", "Expected ')' after print expression.")
        self.expect("SEMICOLON", "Expected ';' after print statement.")
        return PrintStatement(expression, keyword.line, keyword.column)

    def parse_if(self):
        keyword = self.advance()
        self.expect("LPAREN", "Expected '(' after 'if'.")
        condition = self.parse_expression()
        self.expect("RPAREN", "Expected ')' after condition.")
        then_branch = self.parse_block()
        else_branch = None
        if self.current().type == "KEYWORD" and self.current().value == "else":
            self.advance()
            if self.current().type == "KEYWORD" and self.current().value == "if":
                else_branch = [self.parse_if()]
            else:
                else_branch = self.parse_block()
        return IfStatement(condition, then_branch, else_branch, keyword.line, keyword.column)

    def parse_while(self):
        keyword = self.advance()
        self.expect("LPAREN", "Expected '(' after 'while'.")
        condition = self.parse_expression()
        self.expect("RPAREN", "Expected ')' after condition.")
        return WhileStatement(condition, self.parse_block(), keyword.line, keyword.column)

    def parse_block(self):
        self.expect("LBRACE", "Expected '{' to start block.")
        statements = []
        while self.current().type not in ("RBRACE", "EOF"):
            statements.append(self.parse_statement())
        self.expect("RBRACE", "Expected '}' to close block.")
        return statements

    def parse_expression(self):
        return self.parse_logical_or()

    def parse_logical_or(self):
        expression = self.parse_logical_and()
        while self.current().type == "OPERATOR" and self.current().value == "||":
            operator = self.advance()
            expression = BinaryExpression(expression, operator.value, self.parse_logical_and(), operator.line, operator.column)
        return expression

    def parse_logical_and(self):
        expression = self.parse_equality()
        while self.current().type == "OPERATOR" and self.current().value == "&&":
            operator = self.advance()
            expression = BinaryExpression(expression, operator.value, self.parse_equality(), operator.line, operator.column)
        return expression

    def parse_equality(self):
        expression = self.parse_comparison()
        while self.current().type == "OPERATOR" and self.current().value in ("==", "!="):
            operator = self.advance()
            expression = BinaryExpression(expression, operator.value, self.parse_comparison(), operator.line, operator.column)
        return expression

    def parse_comparison(self):
        expression = self.parse_term()
        while self.current().type in ("GREATER", "LESS", "OPERATOR") and self.current().value in (">", "<", ">=", "<="):
            operator = self.advance()
            expression = BinaryExpression(expression, operator.value, self.parse_term(), operator.line, operator.column)
        return expression

    def parse_term(self):
        expression = self.parse_factor()
        while self.current().type in ("PLUS", "MINUS"):
            operator = self.advance()
            expression = BinaryExpression(expression, operator.value, self.parse_factor(), operator.line, operator.column)
        return expression

    def parse_factor(self):
        expression = self.parse_unary()
        while self.current().type in ("STAR", "SLASH", "PERCENT"):
            operator = self.advance()
            expression = BinaryExpression(expression, operator.value, self.parse_unary(), operator.line, operator.column)
        return expression

    def parse_unary(self):
        if self.current().type == "MINUS":
            operator = self.advance()
            return UnaryExpression(operator.value, self.parse_unary(), operator.line, operator.column)
        if self.current().type == "BANG":
            operator = self.advance()
            return UnaryExpression(operator.value, self.parse_unary(), operator.line, operator.column)
        return self.parse_primary()

    def parse_primary(self):
        token = self.current()
        if token.type == "NUMBER":
            self.advance()
            return Number(int(token.value), token.line, token.column)
        if token.type == "FLOAT":
            self.advance()
            return Number(float(token.value), token.line, token.column)
        if token.type == "STRING":
            self.advance()
            return String(token.value, token.line, token.column)
        if token.type in ("TRUE", "FALSE"):
            self.advance()
            return Boolean(token.type == "TRUE", token.line, token.column)
        if token.type == "IDENTIFIER":
            self.advance()
            return Identifier(token.value, token.line, token.column)
        if self.match("LPAREN"):
            expression = self.parse_expression()
            self.expect("RPAREN", "Expected ')' after expression.")
            return expression
        raise SyntaxCompilerError("Expected a number, float, string, boolean, identifier, or parenthesized expression.", token.line, token.column, token.value or token.type)
