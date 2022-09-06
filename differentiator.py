from scan import Scanner
from parse import Parser

if __name__ == '__main__':
    while True:
        i = "Differentiate > "
        scanner = Scanner(input(i))
        tokens = scanner.scan_tokens()
        parser = Parser(tokens)
        expr = parser.expression().simplify()
        diff = expr.differentiate().simplify()
        print(f"{' ' * len(i)}{expr.format()}  ->  {diff.format()}")