"""
Classical interval arithmetic (Moore, 1966).

An Interval is a closed bounded set [lo, hi] with lo <= hi. Each occurrence
of a variable is treated as independent, which produces the well-known
dependency problem: expressions that simplify to a constant (e.g. x - x)
still yield non-trivial ranges.
"""
from __future__ import annotations
import math


class Interval:
    __slots__ = ("lo", "hi")

    def __init__(self, lo: float, hi: float | None = None):
        if hi is None:
            hi = lo
        if lo > hi:
            raise ValueError(f"Invalid interval: lo={lo} > hi={hi}")
        self.lo = float(lo)
        self.hi = float(hi)

    # -------- convenience ----------
    @property
    def width(self) -> float:
        return self.hi - self.lo

    @property
    def mid(self) -> float:
        return 0.5 * (self.lo + self.hi)

    @property
    def rad(self) -> float:
        return 0.5 * self.width

    def range(self) -> tuple[float, float]:
        return (self.lo, self.hi)

    def __repr__(self) -> str:
        return f"Interval[{self.lo:.6g}, {self.hi:.6g}]"

    # -------- arithmetic ----------
    def _as_interval(self, other) -> "Interval":
        if isinstance(other, Interval):
            return other
        return Interval(float(other))

    def __neg__(self):
        return Interval(-self.hi, -self.lo)

    def __add__(self, other):
        o = self._as_interval(other)
        return Interval(self.lo + o.lo, self.hi + o.hi)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        o = self._as_interval(other)
        # Note: each occurrence treated independently — this is the dependency problem.
        return Interval(self.lo - o.hi, self.hi - o.lo)

    def __rsub__(self, other):
        return self._as_interval(other).__sub__(self)

    def __mul__(self, other):
        o = self._as_interval(other)
        prods = (self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi)
        return Interval(min(prods), max(prods))

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        o = self._as_interval(other)
        if o.lo <= 0 <= o.hi:
            raise ZeroDivisionError("Interval divisor contains 0")
        return self * Interval(1.0 / o.hi, 1.0 / o.lo)

    def __rtruediv__(self, other):
        return self._as_interval(other).__truediv__(self)

    def __pow__(self, n: int):
        if not isinstance(n, int) or n < 0:
            raise ValueError("Interval power only for non-negative integers")
        if n == 0:
            return Interval(1.0, 1.0)
        result = self
        for _ in range(n - 1):
            result = result * self
        return result

    # -------- elementary functions (monotonic on domain) ----------
    def exp(self) -> "Interval":
        return Interval(math.exp(self.lo), math.exp(self.hi))

    def log(self) -> "Interval":
        if self.lo <= 0:
            raise ValueError("log requires strictly positive interval")
        return Interval(math.log(self.lo), math.log(self.hi))
