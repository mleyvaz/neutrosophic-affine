"""
Hesitant Neutrosophic Number.

  N_H = a + b * H(I),    H(I) = {I_1, I_2, ..., I_k}    or    H(I) = {[I_min^j, I_max^j]}_{j=1..k}

Each element of H(I) represents an alternative indeterminacy value or
range asserted by a distinct expert or source. Unlike the classical a+bI,
which collapses all hesitancy into a single interval, the hesitant form
preserves the structure of disagreement.

Operations use Torra's (2010) extension principle: given two hesitant sets,
the resulting hesitant set contains the image of all element combinations.

This is the Python realization of the hesitant extension proposed in
Section 5 of Leyva Vazquez & Smarandache (2026).
"""
from __future__ import annotations
from typing import Sequence


class HesitantElement:
    """One element of the hesitant set H(I): either a singleton or an interval."""

    __slots__ = ("lo", "hi")

    def __init__(self, lo: float, hi: float | None = None):
        if hi is None:
            hi = lo
        if lo > hi:
            lo, hi = hi, lo
        if not (0.0 <= lo <= 1.0 and 0.0 <= hi <= 1.0):
            raise ValueError(f"Hesitant element outside [0,1]: [{lo}, {hi}]")
        self.lo = float(lo)
        self.hi = float(hi)

    @property
    def mid(self) -> float:
        return 0.5 * (self.lo + self.hi)

    def __repr__(self) -> str:
        if self.lo == self.hi:
            return f"{self.lo:.3g}"
        return f"[{self.lo:.3g}, {self.hi:.3g}]"


class HesitantNeutrosophic:
    """N_H = a + b * H(I), where H(I) is a set of hesitant elements in [0,1]."""

    __slots__ = ("a", "b", "H")

    def __init__(self, a: float, b: float, H: Sequence):
        self.a = float(a)
        self.b = float(b)
        self.H = tuple(
            h if isinstance(h, HesitantElement) else HesitantElement(*h) if isinstance(h, (tuple, list)) else HesitantElement(h)
            for h in H
        )
        if not self.H:
            raise ValueError("HesitantNeutrosophic: H must contain at least one element")

    def range(self) -> tuple[float, float]:
        """Range is the union envelope of a + b * H over all hesitant elements."""
        if self.b >= 0:
            lo = self.a + self.b * min(h.lo for h in self.H)
            hi = self.a + self.b * max(h.hi for h in self.H)
        else:
            lo = self.a + self.b * max(h.hi for h in self.H)
            hi = self.a + self.b * min(h.lo for h in self.H)
        return (lo, hi)

    def expert_ranges(self) -> list[tuple[float, float]]:
        """Return list of (lo, hi) ranges per hesitant element (per expert)."""
        if self.b >= 0:
            return [(self.a + self.b * h.lo, self.a + self.b * h.hi) for h in self.H]
        return [(self.a + self.b * h.hi, self.a + self.b * h.lo) for h in self.H]

    def score(self, aggregation: str = "mean_mid") -> float:
        """
        Crisp score via aggregation over H(I).

        aggregation:
          "mean_mid"  — arithmetic mean of midpoints of each hesitant element
          "median_mid"— median of midpoints
          "min_lo"    — minimum lower bound (pessimistic)
          "max_hi"    — maximum upper bound (optimistic)
        """
        mids = [h.mid for h in self.H]
        if aggregation == "mean_mid":
            return self.a + self.b * (sum(mids) / len(mids))
        if aggregation == "median_mid":
            s = sorted(mids)
            n = len(s)
            return self.a + self.b * (s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2]))
        if aggregation == "min_lo":
            return self.a + self.b * min(h.lo for h in self.H)
        if aggregation == "max_hi":
            return self.a + self.b * max(h.hi for h in self.H)
        raise ValueError(f"Unknown aggregation: {aggregation}")

    def __repr__(self) -> str:
        sign = "+" if self.b >= 0 else "-"
        return f"HesitantNeutrosophic({self.a:.4g} {sign} {abs(self.b):.4g} * {list(self.H)})"

    # -------- operations via extension principle (Torra 2010) ----------
    def __add__(self, other: "HesitantNeutrosophic") -> "HesitantNeutrosophic":
        """(a1+b1*H1) + (a2+b2*H2) => pairwise combination (Cartesian product reduced)."""
        if not isinstance(other, HesitantNeutrosophic):
            raise TypeError("Hesitant + non-hesitant: convert explicitly first")
        # Cartesian product of hesitant elements; to avoid explosion we reduce to midpoints.
        new_H: list[HesitantElement] = []
        for h1 in self.H:
            for h2 in other.H:
                # Combined range for b1*h1 + b2*h2 in terms of "effective I":
                # We re-project onto [0,1] by normalizing by (|b1| + |b2|).
                total_b = abs(self.b) + abs(other.b)
                if total_b == 0:
                    continue
                sign1 = 1.0 if self.b >= 0 else -1.0
                sign2 = 1.0 if other.b >= 0 else -1.0
                lo = (sign1 * self.b * h1.lo + sign2 * other.b * h2.lo) / total_b if False else \
                    (self.b * h1.lo + other.b * h2.lo) / total_b
                hi = (self.b * h1.hi + other.b * h2.hi) / total_b
                new_H.append(HesitantElement(max(0.0, min(1.0, lo)), max(0.0, min(1.0, hi))))
        return HesitantNeutrosophic(self.a + other.a, abs(self.b) + abs(other.b), new_H)

    def union(self, other: "HesitantNeutrosophic") -> "HesitantNeutrosophic":
        """Union of two hesitant assessments of the same base (same a, b)."""
        if not (self.a == other.a and self.b == other.b):
            raise ValueError("Union requires matching a, b")
        return HesitantNeutrosophic(self.a, self.b, list(self.H) + list(other.H))
