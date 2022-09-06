from typing import Callable


class Token:
    def __repr__(self) -> str:
        return self.__class__.__name__


class Plus(Token):
    pass


class Minus(Token):
    pass


class Multiply(Token):
    pass


class Divide(Token):
    pass


class Exponent(Token):
    pass


class Numeric(Token):
    def __init__(self, num: float) -> None:
        self.num = num

    def __repr__(self) -> str:
        return f"Numeric({self.num})"


class Char(Token):
    def __init__(self, char: str) -> None:
        self.char = char

    def __repr__(self) -> str:
        return f"Char({self.char})"


class OpenBracket(Token):
    pass


class CloseBracket(Token):
    pass


class Scanner:
    def __init__(self, text: str) -> None:
        self.text = text
        self._start = 0
        self._current = 0
        self._tokens: list[Token] = []

    @property
    def is_at_end(self) -> bool:
        return self._current > len(self.text) - 1

    def advance(self) -> str:
        self._current += 1
        return self.text[self._current - 1]

    def peek(self, n: int = 1) -> str:
        return self.text[self._current : self._current + n]

    def consume_while(self, fn: Callable[[int, str], bool]) -> str:
        s = ""
        while fn(self._current, self.peek()):
            s += self.advance()
        return s

    def consume_numeric(self) -> float:
        s = self.consume_while(lambda i, c: c.isnumeric() or c == ".")
        return float(s)

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end:
            self._start = self._current
            self.scan_token()
        return self._tokens

    def scan_token(self):
        c = self.advance()
        match c:
            case "(":
                self.add_token(OpenBracket())
            case ")":
                self.add_token(CloseBracket())
            case "+":
                self.add_token(Plus())
            case "-":
                self.add_token(Minus())
            case "*":
                self.add_token(Multiply())
            case "/":
                self.add_token(Divide())
            case "^":
                self.add_token(Exponent())
            case _ if c.isnumeric():
                self.number()
            case _ if c.isalpha():
                self.char()
            case k if k.isspace():
                pass
            case _:
                print(f"Unknown character {c}")

    def char(self) -> None:
        self.add_token(Char(self.text[self._start : self._current]))

    def number(self) -> None:
        while (c := self.peek()).isnumeric() or c == ".":
            self.advance()
        self.add_token(Numeric(float(self.text[self._start : self._current])))

    def add_token(self, token: Token) -> None:
        self._tokens.append(token)


while True:
    s = input("> ")
    scanner = Scanner(s)
    print(scanner.scan_tokens())
