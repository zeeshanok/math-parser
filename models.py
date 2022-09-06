from dataclasses import dataclass
from typing import Union

SUPERSCRIPTS = {
    '0': '⁰',
    '1': '¹',
    '2': '²',
    '3': '³',
    '4': '⁴',
    '5': '⁵',
    '6': '⁶',
    '7': '⁷',
    '8': '⁸',
    '9': '⁹',
}

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

    def _format(self) -> str:
        raise NotImplementedError()

    def format(self, parent: Union["MathObject", None] = None) -> str:
        s = self._format()
        return bracket_wrap(s) if self._should_bracket_wrap(parent) else s

    def _should_bracket_wrap(self, parent: Union["MathObject", None]) -> bool:
        return False
    
    def _contains_unknown(self) -> bool:
        raise NotImplementedError()


@dataclass
class Constant(MathObject):
    num: float

    def differentiate(self) -> MathObject:
        return Constant(0)

    def _format(self) -> str:
        return f"{self.num:g}"
    
    def _contains_unknown(self) -> bool:
        return False


@dataclass
class Unknown(MathObject):
    char: str = "x"

    def differentiate(self) -> MathObject:
        return Constant(1)

    def _format(self) -> str:
        return self.char
    
    def _contains_unknown(self) -> bool:
        return True

@dataclass
class Addition(MathObject):
    left: MathObject
    right: MathObject

    def _sum_simplify(self, a: MathObject, b: MathObject) -> MathObject | None:
        "Simplification function common to both addition and subtraction"
        if a == Constant(0):
            return b
        if b == Constant(0):
            return a

    def _simplify(self) -> MathObject:
        a, b = self.left._simplify(), self.right._simplify()
        s = self._sum_simplify(a, b) 
        if s is None:
            return Addition(a, b)
        else: return s

    def differentiate(self) -> "Addition":
        return Addition(self.left.differentiate(), self.right.differentiate())

    def _should_bracket_wrap(self, parent: Union["MathObject", None]) -> bool:
        return parent is not None and type(parent)  != Addition

    def _format(self) -> str:
        return f"{self.left.format(self)} + {self.right.format(self)}"
    
    def _contains_unknown(self) -> bool:
        return self.left._contains_unknown() or self.right._contains_unknown()


class Subtraction(Addition):
    def _simplify(self) -> MathObject:
        a, b = self.left._simplify(), self.right._simplify()
        if a == b:
            return Constant(0)
        s = self._sum_simplify(a, b)
        if s is None:
            return Subtraction(a, b)
        else: return s
        
    def differentiate(self) -> "Addition":
        return Subtraction(self.left.differentiate(), self.right.differentiate())

    def _format(self) -> str:
        return f"{self.left.format(self)} - {self.right.format(self)}"
    
    def _should_bracket_wrap(self, parent: Union["MathObject", None]) -> bool:
        return super()._should_bracket_wrap(parent)


@dataclass
class Product(MathObject):

    left: MathObject
    right: MathObject

    def _simplify(self) -> MathObject:
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

    def _should_bracket_wrap(self, parent: Union["MathObject", None]) -> bool:
        return parent is not None and not isinstance(parent, (Addition, Product))

    def _format(self, parent: MathObject | None = None) -> str:
        return f"{self.left.format(self)}•{self.right.format(self)}"

    def _contains_unknown(self) -> bool:
        return self.left._contains_unknown() or self.right._contains_unknown()

@dataclass
class Quotient(MathObject):
    numer: MathObject
    denom: MathObject

    def _simplify(self) -> MathObject:
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

    def _format(self, parent: Union["MathObject", None] = None) -> str:
        return f"{self.numer.format(self)} / {self.denom.format(self)}"

    def _should_bracket_wrap(self, parent: Union["MathObject", None]) -> bool:
        return isinstance(parent, (Product, Power))


@dataclass
class Power(MathObject):
    child: MathObject
    power: MathObject

    def _simplify(self) -> MathObject:
        return (
            self.child._simplify()
            if self.power == Constant(1)
            else Power(self.child._simplify(), self.power)
        )

    def differentiate(self) -> MathObject:
        match self:
            case Power(Constant(), Constant()):
                return Constant(0)
            case Power(x, Constant(n)):
                return Product(Product(Constant(n), Power(x, Constant(n-1))), x.differentiate())
            case _:
                raise NotImplementedError()

    def _format(self, parent: MathObject | None = None) -> str:
        p = f"^{self.power.format(self)}"
        if isinstance(self.power, Constant) and int(self.power.num) == self.power.num:
            s = str(int(self.power.num))
            p = s.translate(s.maketrans(SUPERSCRIPTS))
        return f"{self.child.format(self)}{p}"


if __name__ == "__main__":
    pass