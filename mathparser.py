from models import MathExpression
from scan import Scanner
from parse import Parser

def parse_text(text: str) -> MathExpression:
    return Parser(Scanner(text).scan_tokens()).expression()