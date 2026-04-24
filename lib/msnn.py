"""
Multi-Source Neutrosophic Number (MSNN).

  N = a + sum_{i=1..n} b_i * I_i,    I_i in [0, 1]  mutually independent.

Each I_i is an indeterminacy symbol associated with a distinct source i.
Operations preserve identified sources (shared i's cancel symbolically),
mirroring the noise-symbol machinery of affine arithmetic while retaining
the neutrosophic a + bI notation.

Theorem 2 (Range Equivalence in N-D). For any algebraic expression E
involving n sources of uncertainty, the range computed by MSNN with
independent I_i in [0,1] and by affine arithmetic with n independent noise
symbols e_i in [-1,+1] is identical, under the bijection I_i = (1 + e_i)/2.

This module is the computational realization of Theorem 2 from
Leyva Vazquez & Smarandache (2026).
"""
from __future__ import annotations
import math
from itertools import count as _count

# Global source counter for independent I_i allocation.
_source_counter = _count(start=1)


def reset_source_counter():
    global _source_counter
    _source_counter = _count(start=1)


def new_source_id() -> int:
    return next(_source_counter)


class MSNN:
    """N = a + sum_i b_i * I_i, with I_i in [0,1]."""

    __slots__ = ("a", "terms")

    def __init__(self, a: float, terms: dict[int, float] | None = None):
        self.a = float(a)
        self.terms = {k: float(v) for k, v in (terms or {}).items() if v != 0.0}

    @classmethod
    def from_interval(cls, lo: float, hi: float) -> "MSNN":
        """Create a fresh MSNN representing [lo, hi] with its own source I_k."""
        sid = new_source_id()
        return cls(lo, {sid: hi - lo})

    def range(self) -> tuple[float, float]:
        """Range over I_i in [0,1] independently.

        For each i, b_i * I_i contributes [0, b_i] if b_i >= 0 else [b_i, 0].
        """
        lo_add = sum(min(0.0, v) for v in self.terms.values())
        hi_add = sum(max(0.0, v) for v in self.terms.values())
        return (self.a + lo_add, self.a + hi_add)

    @property
    def lo(self) -> float:
        return self.range()[0]

    @property
    def hi(self) -> float:
        return self.range()[1]

    def score(self, I_expected: float = 0.5) -> float:
        """Crisp score: a + sum_i b_i * I_expected."""
        return self.a + sum(self.terms.values()) * I_expected

    def __repr__(self) -> str:
        parts = [f"{self.a:.4g}"] + [
            f"{v:+.4g}*I{k}" for k, v in sorted(self.terms.items())
        ]
        return "MSNN(" + " ".join(parts) + ")"

    # -------- affine operations (NO new sources) ----------
    def _as_msnn(self, other) -> "MSNN":
        if isinstance(other, MSNN):
            return other
        return MSNN(float(other), {})

    def __neg__(self):
        return MSNN(-self.a, {k: -v for k, v in self.terms.items()})

    def __add__(self, other):
        o = self._as_msnn(other)
        terms = dict(self.terms)
        for k, v in o.terms.items():
            terms[k] = terms.get(k, 0.0) + v
        return MSNN(self.a + o.a, terms)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.__add__(-self._as_msnn(other))

    def __rsub__(self, other):
        return self._as_msnn(other).__sub__(self)

    def __mul__(self, other):
        # scalar multiplication is affine
        if not isinstance(other, MSNN):
            c = float(other)
            return MSNN(self.a * c, {k: v * c for k, v in self.terms.items()})
        o = other
        # Affine linearization at I_i = 0.5 (midpoint), analogous to affine
        # arithmetic's Chebyshev expansion around the center.
        # If we denote a_i = a, b_i = sum(terms_i) then we approximate
        # x*y around (a_x + S_x/2, a_y + S_y/2) with S_x, S_y sums.
        a_x = self.a + 0.5 * sum(self.terms.values())
        a_y = o.a + 0.5 * sum(o.terms.values())
        # Linear coefficient in I_k for each variable:
        # For self: b_k * (a_y) contribution, for other: b_k * a_x
        new_terms: dict[int, float] = {}
        for k, v in self.terms.items():
            new_terms[k] = new_terms.get(k, 0.0) + a_y * v
        for k, v in o.terms.items():
            new_terms[k] = new_terms.get(k, 0.0) + a_x * v
        # Linearization error: bound by product of total-half-deviations
        # (analogous to Stolfi-de Figueiredo error term).
        dev_x = 0.5 * sum(abs(v) for v in self.terms.values())
        dev_y = 0.5 * sum(abs(v) for v in o.terms.values())
        err = dev_x * dev_y * 4  # max |dx * dy| over the box (each in [-rad,+rad])
        # Center constant:
        c0 = a_x * a_y - 0.5 * sum(a_y * v for v in self.terms.values()) \
                       - 0.5 * sum(a_x * v for v in o.terms.values())
        if err > 0:
            new_terms[new_source_id()] = err
            # We encoded the error as a new I_err in [0,1] contributing [0, err].
            # The center shifts by -err/2 so the expected behavior is symmetric.
            c0 -= 0.5 * err
        return MSNN(c0, new_terms)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, MSNN):
            return self * other.reciprocal()
        return self * (1.0 / float(other))

    def __rtruediv__(self, other):
        return self._as_msnn(other) * self.reciprocal()

    def reciprocal(self) -> "MSNN":
        lo, hi = self.range()
        if lo <= 0 <= hi:
            raise ZeroDivisionError("MSNN reciprocal: range contains 0")
        # Work in positive domain; if negative, flip signs.
        if lo > 0:
            a_pos, b_pos, signed_self = lo, hi, self
            sign = 1.0
        else:
            a_pos, b_pos = -hi, -lo
            signed_self = -self
            sign = -1.0
        # Chebyshev for 1/x on [a_pos, b_pos]
        alpha = -1.0 / (a_pos * b_pos)
        y_a, y_b = 1.0 / a_pos, 1.0 / b_pos
        zeta = 0.5 * (y_a + y_b - alpha * (a_pos + b_pos))
        delta = 0.5 * abs(y_a - y_b - alpha * (a_pos - b_pos))
        new_terms = {k: alpha * v for k, v in signed_self.terms.items()}
        result = MSNN(alpha * signed_self.a + zeta, new_terms)
        if delta > 0:
            result.terms[new_source_id()] = delta
            result.a -= 0.5 * delta
        return result if sign > 0 else -result

    def __pow__(self, n: int):
        if not isinstance(n, int) or n < 0:
            raise ValueError("MSNN power: non-negative integer only")
        if n == 0:
            return MSNN(1.0)
        result = self
        for _ in range(n - 1):
            result = result * self
        return result

    # -------- elementary functions (Chebyshev linearization) ----------
    def exp(self) -> "MSNN":
        lo, hi = self.range()
        if math.isclose(lo, hi):
            return MSNN(math.exp(lo))
        y_lo, y_hi = math.exp(lo), math.exp(hi)
        alpha = (y_hi - y_lo) / (hi - lo)
        x_star = math.log(alpha)
        y_star = math.exp(x_star)
        beta = 0.5 * (y_lo + y_star - alpha * (lo + x_star))
        delta = 0.5 * (y_star - y_lo - alpha * (x_star - lo))
        new_terms = {k: alpha * v for k, v in self.terms.items()}
        result = MSNN(alpha * self.a + beta, new_terms)
        if abs(delta) > 0:
            result.terms[new_source_id()] = abs(delta)
            result.a -= 0.5 * abs(delta)
        return result

    def log(self) -> "MSNN":
        lo, hi = self.range()
        if lo <= 0:
            raise ValueError("log requires strictly positive MSNN range")
        if math.isclose(lo, hi):
            return MSNN(math.log(lo))
        alpha = (math.log(hi) - math.log(lo)) / (hi - lo)
        x_star = 1.0 / alpha
        beta = 0.5 * (math.log(lo) + math.log(x_star) - alpha * (lo + x_star))
        delta = 0.5 * (math.log(x_star) - math.log(lo) - alpha * (x_star - lo))
        new_terms = {k: alpha * v for k, v in self.terms.items()}
        result = MSNN(alpha * self.a + beta, new_terms)
        if abs(delta) > 0:
            result.terms[new_source_id()] = abs(delta)
            result.a -= 0.5 * abs(delta)
        return result
