from typing import Type

from models import (
    Addition,
    Constant,
    MathObject,
    Power,
    Product,
    Quotient,
    Subtraction,
    Unknown,
)
from scan import (
    Char,
    CloseBracket,
    Divide,
    Minus,
    Multiply,
    Numeric,
    OpenBracket,
    Plus,
    Scanner,
    Token,
    Exponent,
)

# expression -> term
# term       -> factor ( ( "+" | "-" ) factor )*
# factor     -> exponent ( ( "*" | "/"  ) exponent )*
# exponent   -> ( primary "^" )* exponent
# primary    -> NUMERIC | CHAR | "(" expression ")"


def build_binary_math_object(
    left: MathObject, operator: Token, right: MathObject
) -> MathObject:
    match operator:
        case Plus():
            return Addition(left, right)
        case Minus():
            return Subtraction(left, right)
        case Multiply():
            return Product(left, right)
        case Divide():
            return Quotient(left, right)
        case Exponent():
            return Power(left, right)
        case _:
            raise ValueError(f"invalid operator {operator}")


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    @property
    def is_at_end(self) -> bool:
        return self.current > len(self.tokens) - 1

    def check(self, *types: Type[Token]) -> bool:
        if self.is_at_end:
            return False
        return isinstance(self.peek(), types)

    def advance(self) -> Token:
        self.current += 1
        return self.previous()

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def match(self, *types: Type[Token]) -> bool:
        if self.check(*types):
            self.advance()
            return True
        return False

    def expression(self) -> MathObject:
        return self.term()

    def term(self) -> MathObject:
        expr = self.factor()
        while self.match(Plus, Minus):
            operator = self.previous()
            right = self.factor()
            expr = build_binary_math_object(expr, operator, right)

        return expr

    def factor(self) -> MathObject:
        expr = self.exponent()
        while self.match(Multiply, Divide):
            operator = self.previous()
            right = self.exponent()
            expr = build_binary_math_object(expr, operator, right)

        return expr

    def exponent(self) -> MathObject:
        left = self.primary()
        while self.match(Exponent):
            right = self.exponent()
            left = build_binary_math_object(left, Exponent(), right)
        
        return left

    def primary(self) -> MathObject:
        if self.match(Numeric):
            p = self.previous()
            assert isinstance(p, Numeric)
            return Constant(p.num)

        if self.match(Char):
            p = self.previous()
            assert isinstance(p, Char)
            return Unknown(p.char)

        if self.match(OpenBracket):
            expr = self.expression()
            if not self.match(CloseBracket):
                raise ValueError("Missing ')' character")
            return expr

        raise ValueError("How did we get here")

if __name__ == '__main__':
    while True:
        scanner = Scanner(input("> "))
        tokens = scanner.scan_tokens()
        print(tokens)
        p = Parser(tokens)
        expr = p.expression()
        print(expr)
