from mathparser import parse_text

if __name__ == '__main__':
    i = '>  '
    b = '='.ljust(len(i))
    while True:
        expr = parse_text(input(i))
        unknown_map = {i: float(input(f"{i}: ")) for i in expr.get_unknowns()}
        try:
            answer = expr.evaluate(unknown_map)
            print(f'{b}{answer:g}')
        except ValueError as e:
            print(e)
