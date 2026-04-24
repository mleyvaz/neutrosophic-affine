"""
Affine arithmetic (Stolfi & de Figueiredo, 1993).

An affine form is x_hat = x0 + sum_{i=1..n} x_i * e_i,
where x0 is the central value, x_i are real coefficients, and e_i are
independent noise symbols with values in [-1, +1].

Each e_i identifies a specific source of uncertainty. Shared sources across
operations produce shared symbols, which allows the formalism to cancel
dependencies during computation.

Non-affine operations (multiplication, division, exp, ...) are linearized
using Chebyshev (min-max) approximations and a fresh noise symbol carries
the linearization error.
"""
from __future__ import annotations
import math
from itertools import count as _count

# Global noise-symbol counter. Call reset_noise_counter() between independent
# benchmarks to ensure reproducibility.
_noise_counter = _count(start=1)


def reset_noise_counter():
    global _noise_counter
    _noise_counter = _count(start=1)


def new_noise_id() -> int:
    return next(_noise_counter)


class Affine:
    """x_hat = x0 + sum_i x_i * e_i  with e_i in [-1, +1]."""

    __slots__ = ("x0", "terms")

    def __init__(self, x0: float, terms: dict[int, float] | None = None):
        self.x0 = float(x0)
        # {noise_id: coefficient}. Zero coefs filtered.
        self.terms = {k: float(v) for k, v in (terms or {}).items() if v != 0.0}

    # -------- convenience ----------
    @classmethod
    def from_interval(cls, lo: float, hi: float) -> "Affine":
        """Create a fresh affine form that represents [lo, hi] with its own noise symbol."""
        mid = 0.5 * (lo + hi)
        rad = 0.5 * (hi - lo)
        nid = new_noise_id()
        return cls(mid, {nid: rad})

    def total_deviation(self) -> float:
        """Sum of |x_i|, giving the half-width of the bounding interval."""
        return sum(abs(v) for v in self.terms.values())

    def range(self) -> tuple[float, float]:
        d = self.total_deviation()
        return (self.x0 - d, self.x0 + d)

    @property
    def lo(self) -> float:
        return self.x0 - self.total_deviation()

    @property
    def hi(self) -> float:
        return self.x0 + self.total_deviation()

    def __repr__(self) -> str:
        parts = [f"{self.x0:.4g}"] + [f"{v:+.4g}*e{k}" for k, v in sorted(self.terms.items())]
        return "Affine(" + " ".join(parts) + ")"

    # -------- affine operations (NO new noise symbols) ----------
    def _as_affine(self, other) -> "Affine":
        if isinstance(other, Affine):
            return other
        return Affine(float(other))

    def __neg__(self):
        return Affine(-self.x0, {k: -v for k, v in self.terms.items()})

    def __add__(self, other):
        o = self._as_affine(other)
        terms = dict(self.terms)
        for k, v in o.terms.items():
            terms[k] = terms.get(k, 0.0) + v
        return Affine(self.x0 + o.x0, terms)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.__add__(-self._as_affine(other))

    def __rsub__(self, other):
        return self._as_affine(other).__sub__(self)

    def __mul__(self, other):
        # scalar * affine: remains affine (no linearization needed)
        if not isinstance(other, Affine):
            c = float(other)
            return Affine(self.x0 * c, {k: v * c for k, v in self.terms.items()})
        # affine * affine: non-affine. Use Chebyshev linearization with fresh noise.
        o = other
        x0, y0 = self.x0, o.x0
        # linear part: y0*x_hat_centered + x0*y_hat_centered + x0*y0
        new_terms: dict[int, float] = {}
        for k, v in self.terms.items():
            new_terms[k] = new_terms.get(k, 0.0) + y0 * v
        for k, v in o.terms.items():
            new_terms[k] = new_terms.get(k, 0.0) + x0 * v
        # quadratic error bound: total_deviation(self) * total_deviation(o)
        err = self.total_deviation() * o.total_deviation()
        if err > 0:
            new_terms[new_noise_id()] = err
        return Affine(x0 * y0, new_terms)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, Affine):
            return self * other.reciprocal()
        return self * (1.0 / float(other))

    def __rtruediv__(self, other):
        return self._as_affine(other) * self.reciprocal()

    def reciprocal(self) -> "Affine":
        """1/x via Chebyshev min-max affine approximation on [lo, hi]."""
        lo, hi = self.range()
        if lo <= 0 <= hi:
            raise ZeroDivisionError("Affine reciprocal: range contains 0")
        if lo > 0:
            a, b = lo, hi
        else:
            a, b = -hi, -lo  # Work in positive domain, flip sign at end.
            sign = -1
            # Adjust self.x0 sign for the computation, then flip.
            # Simpler: handle negative range by applying f(x)=1/x analytically.
        # Chebyshev on f(x)=1/x over [a,b]>0: best affine approx y = alpha*x + beta,
        # with alpha = -1/(a*b), beta = 0.5*(1/a + 1/b + alpha*(a+b)/2)...
        # We use the standard derivation from Stolfi-de Figueiredo Sec 5.
        alpha = -1.0 / (a * b)
        y_a, y_b = 1.0 / a, 1.0 / b
        # max-error formula:
        zeta = 0.5 * (y_a + y_b - alpha * (a + b))
        delta = 0.5 * abs(y_a - y_b - alpha * (a - b))
        # Now 1/x ~ alpha*x + zeta +/- delta over [a,b]
        if lo > 0:
            result = Affine(alpha * self.x0 + zeta, {k: alpha * v for k, v in self.terms.items()})
            if delta > 0:
                result.terms[new_noise_id()] = delta
            return result
        # Negative domain: 1/x = -1/(-x). Compute on -self.
        neg = -self
        return -neg.reciprocal()

    def __pow__(self, n: int):
        if not isinstance(n, int) or n < 0:
            raise ValueError("Affine power only for non-negative integers")
        if n == 0:
            return Affine(1.0)
        result = self
        for _ in range(n - 1):
            result = result * self
        return result

    # -------- elementary functions ----------
    def exp(self) -> "Affine":
        """Chebyshev linearization of exp over [lo, hi]."""
        lo, hi = self.range()
        if math.isclose(lo, hi):
            return Affine(math.exp(lo))
        y_lo, y_hi = math.exp(lo), math.exp(hi)
        alpha = (y_hi - y_lo) / (hi - lo)
        # Minimax: pick x* where exp'(x*) = alpha, i.e., x* = ln(alpha)
        x_star = math.log(alpha)
        y_star = math.exp(x_star)
        # Affine approximation: y = alpha*x + beta +/- delta
        # beta = 0.5 * (y_lo + y_star - alpha*(lo + x_star))
        beta = 0.5 * (y_lo + y_star - alpha * (lo + x_star))
        delta = 0.5 * (y_star - y_lo - alpha * (x_star - lo))
        result = Affine(alpha * self.x0 + beta, {k: alpha * v for k, v in self.terms.items()})
        if abs(delta) > 0:
            result.terms[new_noise_id()] = abs(delta)
        return result

    def log(self) -> "Affine":
        """Chebyshev linearization of log over [lo, hi] > 0."""
        lo, hi = self.range()
        if lo <= 0:
            raise ValueError("log requires strictly positive affine form")
        if math.isclose(lo, hi):
            return Affine(math.log(lo))
        alpha = (math.log(hi) - math.log(lo)) / (hi - lo)
        x_star = 1.0 / alpha
        beta = 0.5 * (math.log(lo) + math.log(x_star) - alpha * (lo + x_star))
        delta = 0.5 * (math.log(x_star) - math.log(lo) - alpha * (x_star - lo))
        result = Affine(alpha * self.x0 + beta, {k: alpha * v for k, v in self.terms.items()})
        if abs(delta) > 0:
            result.terms[new_noise_id()] = abs(delta)
        return result
