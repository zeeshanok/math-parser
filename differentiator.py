from mathparser import parse_text

if __name__ == '__main__':
    while True:
        i = "Differentiate > "
        expr = parse_text(input(i))
        diff = expr.differentiate().simplify()
        print(f"{' ' * len(i)}{expr.format()}  ->  {diff.format()}")