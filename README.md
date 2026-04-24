# Neutrosophic vs Affine Arithmetic — Reference Implementation

Companion code for:

> Leyva Vázquez, M. Y., & Smarandache, F. (2026).
> **Neutrosophic Interval-Indeterminate Numbers of the Form a + bI: A Comparative
> Analysis with Interval and Affine Arithmetic, with Multi-Source and Hesitant
> Extensions.**

## Structure

```
Neutrosophic_Affine_Project/
├── lib/
│   ├── __init__.py
│   ├── interval.py       — Classical interval [a, b]
│   ├── affine.py         — Affine form x₀ + Σ xᵢ·eᵢ
│   ├── neutrosophic.py   — Classical a + b·I
│   ├── msnn.py           — Multi-Source N = a + Σ bᵢ·Iᵢ
│   └── hesitant.py       — Hesitant N_H = a + b·H(I)
├── tests/
│   └── test_basic.py     — Sanity tests (Theorems 1 and 2 verified empirically)
├── benchmarks/
│   ├── bench_all.py      — 15-expression benchmark
│   └── bench_results.csv
├── figures/
│   ├── fig1_dependency.py
│   ├── fig2_hesitant.py
│   ├── fig3_benchmark.py
│   ├── fig4_decision.py
│   └── *.png
└── paper/
    ├── generate_paper_v2.py
    └── Paper_V2_Neutrosophic_vs_Affine.docx
```

## Quick start

```python
from lib import Interval, Affine, Neutrosophic, MSNN, HesitantNeutrosophic

# 1. Classical interval — suffers from dependency problem
x = Interval(100, 105)
print((x - x).range())   # → (-5.0, 5.0) spurious

# 2. Affine — cancels shared noise
from lib import reset_noise_counter
reset_noise_counter()
x_hat = Affine.from_interval(100, 105)
print((x_hat - x_hat).range())   # → (0.0, 0.0) exact

# 3. Classical neutrosophic a + bI — cancels symbolic I
N = Neutrosophic.from_interval(100, 105)
print((N - N))   # → Neutrosophic(0 + 0*I)

# 4. Multi-source MSNN — tracks independent sources
from lib.msnn import reset_source_counter
reset_source_counter()
x = MSNN.from_interval(10, 20)    # → a + b₁·I₁
y = MSNN.from_interval(5, 10)     # → a + b₂·I₂
print((x + y - x).range())        # → (5.0, 10.0) — 'x' cancels, 'y' preserved

# 5. Hesitant — preserves expert-level disagreement
N_H = HesitantNeutrosophic(120, 15, [(0.0, 0.67), (0.33, 1.0), (0.0, 0.53)])
print(N_H.score("mean_mid"))      # → 126.325
```

## Reproducing the paper

```bash
python tests/test_basic.py        # Empirical verification of Theorems 1 and 2
python benchmarks/bench_all.py    # Generate bench_results.csv
python figures/fig1_dependency.py # Figure 1
python figures/fig2_hesitant.py   # Figure 2
python figures/fig3_benchmark.py  # Figure 3
python figures/fig4_decision.py   # Figure 4
python paper/generate_paper_v2.py # Paper V2 .docx
```

## Key results

**Theorem 1 (1D).** Range equivalence between `a + bI` and affine arithmetic under
`I = (1 + e)/2`. Empirically verified on 5 representative expressions.

**Theorem 2 (N-D).** MSNN `N = a + Σᵢ bᵢ·Iᵢ` achieves N-dimensional range
equivalence with affine arithmetic via independent source identifiers,
preserving the semantic transparency of `a + bI`. Empirically verified on
5 two-source expressions.

**Hesitant extension.** `N_H = a + b · H(I)` with extension-principle operators
captures expert disagreement that neither interval nor native affine arithmetic
can represent. Four explicit score-aggregation conventions (mean-mid, median-mid,
min-lo, max-hi).

**Benchmarks.** 15 algebraic expressions across 5 categories. Interval arithmetic
overestimates by up to 400% in repeated-variable expressions; affine, a + bI,
and MSNN produce identical ranges for all affine-only expressions.

## License

MIT. Cite the companion paper when using this code in academic work.
