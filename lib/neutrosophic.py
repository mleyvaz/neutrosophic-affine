"""
Classical neutrosophic interval-indeterminate numbers a + bI.

A neutrosophic number is N = a + b*I, where:
  - a is the determinate part,
  - b is a real coefficient,
  - I is the indeterminacy symbol, with value in [0, 1].

Operations treat I symbolically: I + I = 2I, I - I = 0, c*I = cI for constant c.
Under the idempotent convention (Smarandache, 2003; Kandasamy & Smarandache,
2006), I*I = I. The range of N = a + bI is:
  - [a, a+b] if b >= 0
  - [a+b, a] if b < 0

This is the canonical one-variable form. For multiple independent sources,
see msnn.MSNN.
"""
from __future__ import annotations
import math


class Neutrosophic:
    """N = a + b*I, with I in [0, 1]."""

    __slots__ = ("a", "b")

    def __init__(self, a: float, b: float = 0.0):
        self.a = float(a)
        self.b = float(b)

    @classmethod
    def from_interval(cls, lo: float, hi: float) -> "Neutrosophic":
        """Create a + bI that spans [lo, hi]. a = lo, b = hi - lo."""
        return cls(lo, hi - lo)

    def range(self) -> tuple[float, float]:
        if self.b >= 0:
            return (self.a, self.a + self.b)
        return (self.a + self.b, self.a)

    @property
    def lo(self) -> float:
        return self.range()[0]

    @property
    def hi(self) -> float:
        return self.range()[1]

    def score(self, I_expected: float = 0.5) -> float:
        """Crisp score: a + b * I_expected. Default I_expected = 0.5 (uniform)."""
        return self.a + self.b * I_expected

    def __repr__(self) -> str:
        sign = "+" if self.b >= 0 else "-"
        return f"Neutrosophic({self.a:.6g} {sign} {abs(self.b):.6g}*I)"

    # -------- arithmetic ----------
    def _as_n(self, other) -> "Neutrosophic":
        if isinstance(other, Neutrosophic):
            return other
        return Neutrosophic(float(other), 0.0)

    def __neg__(self):
        return Neutrosophic(-self.a, -self.b)

    def __add__(self, other):
        o = self._as_n(other)
        return Neutrosophic(self.a + o.a, self.b + o.b)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        o = self._as_n(other)
        # Symbolic: (a1+b1I) - (a2+b2I) = (a1-a2) + (b1-b2)I
        # In particular, N - N = 0 exactly.
        return Neutrosophic(self.a - o.a, self.b - o.b)

    def __rsub__(self, other):
        return self._as_n(other).__sub__(self)

    def __mul__(self, other):
        if not isinstance(other, Neutrosophic):
            c = float(other)
            return Neutrosophic(self.a * c, self.b * c)
        # Idempotent I: I*I = I
        # (a1+b1I)(a2+b2I) = a1a2 + (a1b2 + a2b1 + b1b2)I
        o = other
        return Neutrosophic(self.a * o.a, self.a * o.b + o.a * self.b + self.b * o.b)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if not isinstance(other, Neutrosophic):
            c = float(other)
            return Neutrosophic(self.a / c, self.b / c)
        # Use range-based linearization since symbolic 1/(a+bI) is not closed.
        o = other
        lo, hi = o.range()
        if lo <= 0 <= hi:
            raise ZeroDivisionError("Neutrosophic division: range contains 0")
        # Reciprocal approximation: range [1/hi, 1/lo], then multiply
        recip = Neutrosophic.from_interval(1.0 / hi, 1.0 / lo)
        return self * recip

    def __rtruediv__(self, other):
        return self._as_n(other).__truediv__(self)

    def __pow__(self, n: int):
        if not isinstance(n, int) or n < 0:
            raise ValueError("Neutrosophic power: non-negative integer only")
        if n == 0:
            return Neutrosophic(1.0, 0.0)
        result = self
        for _ in range(n - 1):
            result = result * self
        return result

    # -------- elementary functions (via range linearization) ----------
    def exp(self) -> "Neutrosophic":
        lo, hi = self.range()
        return Neutrosophic.from_interval(math.exp(lo), math.exp(hi))

    def log(self) -> "Neutrosophic":
        lo, hi = self.range()
        if lo <= 0:
            raise ValueError("log requires strictly positive range")
        return Neutrosophic.from_interval(math.log(lo), math.log(hi))
