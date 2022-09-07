from dataclasses import dataclass
from typing import Union

SUPERSCRIPTS = {
    "0": "⁰",
    "1": "¹",
    "2": "²",
    "3": "³",
    "4": "⁴",
    "5": "⁵",
    "6": "⁶",
    "7": "⁷",
    "8": "⁸",
    "9": "⁹",
}


def bracket_wrap(s: str):
    return f"({s})"


class MathExpression:
    def _simplify(self) -> "MathExpression":
        return self

    def simplify(self) -> "MathExpression":
        a = self._simplify()
        b = a._simplify()
        while a != b:
            a, b = b, b._simplify()
        return a

    def differentiate(self) -> "MathExpression":
        raise NotImplementedError()

    def _format(self) -> str:
        raise NotImplementedError()

    def format(self, parent: Union["MathExpression", None] = None) -> str:
        s = self._format()
        return bracket_wrap(s) if self._should_bracket_wrap(parent) else s

    def _should_bracket_wrap(self, parent: Union["MathExpression", None]) -> bool:
        return False

    def get_unknowns(self) -> set[str]:
        "Returns the unknowns that exist in this chain of MathExpressions or an empty set if none exist."
        raise NotImplementedError()

    def evaluate(self, unknown_map: dict[str, float]) -> float:
        """
        Computes the value of a composition of `MathExpression` objects.
        `unknown_map` is a dictionary mapping unknowns to their substituted values
        """
        raise NotImplementedError()


@dataclass
class Constant(MathExpression):
    num: float

    def differentiate(self) -> MathExpression:
        return Constant(0)

    def _format(self) -> str:
        return f"{self.num:g}"

    def get_unknowns(self) -> set[str]:
        return set()

    def evaluate(self, unknown_map: dict[str, float]) -> float:
        return self.num


@dataclass
class Unknown(MathExpression):
    char: str = "x"

    def differentiate(self) -> MathExpression:
        return Constant(1)

    def _format(self) -> str:
        return self.char

    def get_unknowns(self) -> set[str]:
        return {self.char}

    def evaluate(self, unknown_map: dict[str, float]) -> float:
        return unknown_map[self.char]


@dataclass
class Addition(MathExpression):
    left: MathExpression
    right: MathExpression

    def _sum_simplify(
        self, a: MathExpression, b: MathExpression
    ) -> MathExpression | None:
        "Simplification function common to both addition and subtraction"
        if a == Constant(0):
            return b
        if b == Constant(0):
            return a

    def _simplify(self) -> MathExpression:
        a, b = self.left._simplify(), self.right._simplify()
        s = self._sum_simplify(a, b)
        if s is None:
            return Addition(a, b)
        else:
            return s

    def differentiate(self) -> "Addition":
        return Addition(self.left.differentiate(), self.right.differentiate())

    def evaluate(self, unknown_map: dict[str, float]) -> float:
        return self.left.evaluate(unknown_map) + self.right.evaluate(unknown_map)

    def _should_bracket_wrap(self, parent: Union["MathExpression", None]) -> bool:
        return parent is not None and type(parent) != Addition

    def _format(self) -> str:
        return f"{self.left.format(self)} + {self.right.format(self)}"

    def get_unknowns(self) -> set[str]:
        return self.left.get_unknowns() | self.right.get_unknowns()


class Subtraction(Addition):
    def _simplify(self) -> MathExpression:
        a, b = self.left._simplify(), self.right._simplify()
        if a == b:
            return Constant(0)
        s = self._sum_simplify(a, b)
        if s is None:
            return Subtraction(a, b)
        else:
            return s

    def differentiate(self) -> "Addition":
        return Subtraction(self.left.differentiate(), self.right.differentiate())

    def evaluate(self, unknown_map: dict[str, float]) -> float:
        return self.left.evaluate(unknown_map) - self.right.evaluate(unknown_map)

    def _format(self) -> str:
        return f"{self.left.format(self)} - {self.right.format(self)}"

    def _should_bracket_wrap(self, parent: Union["MathExpression", None]) -> bool:
        return super()._should_bracket_wrap(parent)


@dataclass
class Product(MathExpression):

    left: MathExpression
    right: MathExpression

    def _simplify(self) -> MathExpression:
        a, b = self.left._simplify(), self.right._simplify()
        if a == Constant(0) or b == Constant(0):
            return Constant(0)
        if a == Constant(1):
            return b
        if b == Constant(1):
            return a

        return Product(a, b)

    def differentiate(self) -> Addition:
        return Addition(
            Product(self.left.differentiate(), self.right),
            Product(self.left, self.right.differentiate()),
        )

    def evaluate(self, unknown_map: dict[str, float]) -> float:
        return self.left.evaluate(unknown_map) * self.right.evaluate(unknown_map)

    def _should_bracket_wrap(self, parent: Union["MathExpression", None]) -> bool:
        return parent is not None and not isinstance(parent, (Addition, Product))

    def _format(self, parent: MathExpression | None = None) -> str:
        return f"{self.left.format(self)}•{self.right.format(self)}"

    def get_unknowns(self) -> set[str]:
        return self.left.get_unknowns() | self.right.get_unknowns()


@dataclass
class Quotient(MathExpression):
    numer: MathExpression
    denom: MathExpression

    def _simplify(self) -> MathExpression:
        if self.numer == self.denom:
            return Constant(1)
        return Quotient(self.numer._simplify(), self.denom._simplify())

    def differentiate(self) -> "Quotient":
        return Quotient(
            Subtraction(
                Product(self.denom, self.numer.differentiate()),
                Product(self.numer, self.denom.differentiate()),
            ),
            Power(self.denom, Constant(2)),
        )

    def evaluate(self, unknown_map: dict[str, float]) -> float:
        return self.numer.evaluate(unknown_map) / self.denom.evaluate(unknown_map)

    def _format(self, parent: Union["MathExpression", None] = None) -> str:
        return f"{self.numer.format(self)} / {self.denom.format(self)}"

    def _should_bracket_wrap(self, parent: Union["MathExpression", None]) -> bool:
        return isinstance(parent, (Product, Power))

    def get_unknowns(self) -> set[str]:
        return self.numer.get_unknowns() | self.denom.get_unknowns()


@dataclass
class Power(MathExpression):
    base: MathExpression
    power: MathExpression

    def _simplify(self) -> MathExpression:
        return (
            self.base._simplify()
            if self.power == Constant(1)
            else Power(self.base._simplify(), self.power)
        )

    def differentiate(self) -> MathExpression:
        match self:
            case Power(Constant(), Constant()):
                return Constant(0)
            case Power(x, Constant(n)):
                return Product(
                    Product(Constant(n), Power(x, Constant(n - 1))), x.differentiate()
                )
            case _:
                raise NotImplementedError()

    def evaluate(self, unknown_map: dict[str, float]) -> float:
        return self.base.evaluate(unknown_map) ** self.power.evaluate(unknown_map)

    def get_unknowns(self) -> set[str]:
        return self.base.get_unknowns() | self.power.get_unknowns()

    def _format(self, parent: MathExpression | None = None) -> str:
        p = f"^{self.power.format(self)}"
        if isinstance(self.power, Constant) and int(self.power.num) == self.power.num:
            s = str(int(self.power.num))
            p = s.translate(s.maketrans(SUPERSCRIPTS))
        return f"{self.base.format(self)}{p}"


if __name__ == "__main__":
    pass

# troll
