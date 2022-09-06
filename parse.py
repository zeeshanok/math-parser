from .scan import Token

class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
    
    def parse(self):
        pass