from dataclasses import dataclass
from typing import Union


def bracket_wrap(s: str):
    return f"({s})"


class MathObject:
    def _simplify(self) -> "MathObject":
        return self

    def simplify(self) -> "MathObject":
        a = self._simplify()
        b = a._simplify()
        while a != b:
            a, b = b, b._simplify()
        return a

    def differentiate(self) -> "MathObject":
        raise NotImplementedError()

    def format(self, parent: Union["MathObject", None] = None) -> str:
        raise NotImplementedError()


@dataclass
class Constant(MathObject):
    num: float

    def differentiate(self) -> MathObject:
        return Constant(0)

    def format(self, parent: MathObject | None = None) -> str:
        return f"{self.num:g}"


@dataclass
class Unknown(MathObject):
    term: str = "x"

    def differentiate(self) -> MathObject:
        return Constant(1)

    def format(self, parent: MathObject | None = None) -> str:
        return f"{self.term}"


@dataclass
class Sum(MathObject):
    terms: list[MathObject]

    def _simplify(self) -> "Sum":
        return Sum([t._simplify() for t in self.terms if t != Constant(0)])

    def differentiate(self) -> "Sum":
        return Sum([t.differentiate() for t in self.terms])

    def format(self, parent: MathObject | None = None) -> str:
        s = " + ".join(i.format(self) for i in self.terms)
        return (
            bracket_wrap(s)
            if parent is not None and not isinstance(parent, (Sum, Quotient))
            else s
        )


@dataclass
class Product(MathObject):
    terms: list[MathObject]

    def _simplify(self) -> MathObject:
        p = [t._simplify() for t in self.terms if t != Constant(1)]
        return Constant(0) if any(i == Constant(0) for i in p) else Product(p)

    def differentiate(self) -> Sum:
        return Sum(
            [
                Product(
                    [
                        *self.terms[:i],
                        self.terms[i].differentiate(),
                        *self.terms[i + 1 :],
                    ]
                )
                for i in range(len(self.terms))
            ]
        )

    def format(self, parent: MathObject | None = None) -> str:
        s = "•".join(i.format(self) for i in self.terms)

        return (
            bracket_wrap(s) if parent is not None and not isinstance(parent, Sum) else s
        )


@dataclass
class Power(MathObject):
    child: MathObject
    power: float

    def _simplify(self) -> MathObject:
        return (
            self.child._simplify()
            if self.power == 1
            else Power(self.child._simplify(), self.power)
        )

    def differentiate(self) -> Product:
        return Product(
            [
                Constant(self.power),
                Power(self.child, self.power - 1),
                self.child.differentiate(),
            ]
        )

    def format(self, parent: MathObject | None = None) -> str:
        return f"{self.child.format(self)}^{self.power:g}"


@dataclass
class Quotient(MathObject):
    numer: MathObject
    denom: MathObject

    def _simplify(self) -> "Quotient":
        return Quotient(self.numer._simplify(), self.denom._simplify())

    def differentiate(self) -> "Quotient":
        return Quotient(
            Sum(
                [
                    Product([self.denom, self.numer.differentiate()]),
                    Product([Constant(-1), self.numer, self.denom.differentiate()]),
                ]
            ),
            Power(self.denom, 2),
        )

    def format(self, parent: Union["MathObject", None] = None) -> str:
        return f"({self.numer.format(self)}) / ({self.denom.format(self)})"


@dataclass
class Equation:
    lhs: MathObject
    rhs: MathObject

    def __str__(self) -> str:
        return f"{self.lhs} = {self.rhs}"


#     Power(
#         Product(
#             [
#                 Constant(5),
#                 Unknown(),
#             ]
#         ),
#         4,
#     ).format()
# )

e = Power(
    Sum(
        [Power(Unknown(), 5), Power(Unknown(), 12), Constant(8)],
    ),
    2,
)
print(e.format())
print(e.differentiate().simplify().format())

k = Quotient(
    Sum([Unknown(), Constant(1)]),
    Sum(
        [
            Product([Constant(2), Unknown()]),
            Constant(4),
        ],
    ),
)
print(k.format())
print(k.differentiate().simplify().format())
