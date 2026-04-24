"""
Comprehensive benchmark: 15 algebraic expressions evaluated across
Interval, Affine, Classical Neutrosophic (a+bI), MSNN (multi-source).

Metrics reported per expression:
  - range width   (smaller = tighter, closer to exact)
  - CPU time (microseconds, median of N repetitions)
  - number of "extra symbols" used (complexity proxy)

Results written to bench_results.csv for Figure 3.
"""
import sys, os, time, csv, statistics, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib import Interval, Affine, Neutrosophic, MSNN, reset_noise_counter
from lib.msnn import reset_source_counter


# 15 expressions. Each is a function f(*xs) where xs are the uncertain variables.
# Each expression declares: name, function, input intervals, exact_range (if closed-form).
BENCHMARKS = [
    # === AFFINE-ONLY (should be equivalent across a+bI, MSNN, Affine) ===
    ("E01 identity",    1, lambda x: x,                        [(10, 20)], (10.0, 20.0)),
    ("E02 linear 2x+3", 1, lambda x: 2*x + 3,                  [(10, 20)], (23.0, 43.0)),
    ("E03 x-x",         1, lambda x: x - x,                    [(10, 20)], (0.0, 0.0)),
    ("E04 2x-x",        1, lambda x: 2*x - x,                  [(10, 20)], (10.0, 20.0)),
    ("E05 (x+5)-(x-3)", 1, lambda x: (x + 5) - (x - 3),        [(10, 20)], (8.0, 8.0)),
    # === TWO VARIABLES, AFFINE-ONLY ===
    ("E06 x+y",         2, lambda x, y: x + y,                 [(10, 20), (5, 10)], (15.0, 30.0)),
    ("E07 x-y",         2, lambda x, y: x - y,                 [(10, 20), (5, 10)], (0.0, 15.0)),
    ("E08 x+y-x",       2, lambda x, y: x + y - x,             [(10, 20), (5, 10)], (5.0, 10.0)),
    ("E09 2x+3y-x-y",   2, lambda x, y: 2*x + 3*y - x - y,     [(10, 20), (5, 10)], (20.0, 40.0)),
    # === NON-AFFINE: multiplication with single variable ===
    ("E10 x*x",         1, lambda x: x * x,                    [(1, 3)], (1.0, 9.0)),
    ("E11 (x-1)(x+1)",  1, lambda x: (x - 1) * (x + 1),        [(1, 3)], (0.0, 8.0)),
    ("E12 (x-10)(x+10)",1, lambda x: (x - 10) * (x + 10),      [(1, 3)], (-99.0, -91.0)),
    # === NON-AFFINE: reciprocal / division ===
    ("E13 1/x",         1, lambda x: 1 / x,                    [(1, 10)], (0.1, 1.0)),
    ("E14 x/(x+1)",     1, lambda x: x / (x + 1),              [(1, 10)], (0.5, 10.0/11.0)),
    # === NON-AFFINE: multiple variables ===
    ("E15 x*y-x*y",     2, lambda x, y: x * y - x * y,         [(1, 3), (2, 4)], (0.0, 0.0)),
]


def measure(build_args, func, reset=None, reps=200):
    """Time the evaluation. Return (range_width, lo, hi, microseconds_median, extras)."""
    times = []
    for _ in range(reps):
        if reset:
            reset()
        args = [build(*iv) for build, iv in build_args]
        t0 = time.perf_counter_ns()
        try:
            result = func(*args)
            # Normalize range extraction
            if hasattr(result, "range") and callable(result.range):
                lo, hi = result.range()
            elif isinstance(result, Neutrosophic):
                lo, hi = result.range()
            else:
                lo = hi = float(result)
        except ZeroDivisionError:
            return None
        t1 = time.perf_counter_ns()
        times.append((t1 - t0) / 1000.0)  # microseconds
    return (hi - lo, lo, hi, statistics.median(times))


def run_benchmarks():
    rows = []
    header = [
        "ID", "Expr", "Vars",
        "Exact_width", "Interval_width", "Affine_width", "Neutro_width", "MSNN_width",
        "Interval_us", "Affine_us", "Neutro_us", "MSNN_us",
        "Interval_overest", "Affine_overest", "Neutro_overest", "MSNN_overest",
    ]
    rows.append(header)

    for name, nvars, func, inputs, exact in BENCHMARKS:
        exact_width = exact[1] - exact[0]

        # --- Interval ---
        res_i = measure(
            [(lambda lo, hi: Interval(lo, hi), iv) for iv in inputs],
            func, reset=None
        )

        # --- Affine ---
        res_a = measure(
            [(lambda lo, hi: Affine.from_interval(lo, hi), iv) for iv in inputs],
            func, reset=reset_noise_counter
        )

        # --- Classical a+bI ---  (only for 1-var expressions, since Neutrosophic is single-source)
        if nvars == 1:
            res_n = measure(
                [(lambda lo, hi: Neutrosophic.from_interval(lo, hi), iv) for iv in inputs],
                func, reset=None
            )
        else:
            res_n = None

        # --- MSNN ---
        res_m = measure(
            [(lambda lo, hi: MSNN.from_interval(lo, hi), iv) for iv in inputs],
            func, reset=reset_source_counter
        )

        def overest(w):
            if exact_width == 0:
                return w  # absolute excess when exact is 0
            return (w - exact_width) / exact_width * 100.0  # percent

        row = [
            name.split(" ")[0],           # ID
            name.split(" ", 1)[1],         # Expr
            nvars,
            f"{exact_width:.4f}",
            f"{res_i[0]:.4f}" if res_i else "NA",
            f"{res_a[0]:.4f}" if res_a else "NA",
            f"{res_n[0]:.4f}" if res_n else "NA",
            f"{res_m[0]:.4f}" if res_m else "NA",
            f"{res_i[3]:.2f}" if res_i else "NA",
            f"{res_a[3]:.2f}" if res_a else "NA",
            f"{res_n[3]:.2f}" if res_n else "NA",
            f"{res_m[3]:.2f}" if res_m else "NA",
            f"{overest(res_i[0]):.1f}" if res_i else "NA",
            f"{overest(res_a[0]):.1f}" if res_a else "NA",
            f"{overest(res_n[0]):.1f}" if res_n else "NA",
            f"{overest(res_m[0]):.1f}" if res_m else "NA",
        ]
        rows.append(row)

    out_csv = os.path.join(os.path.dirname(__file__), "bench_results.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    # Pretty print
    widths = [max(len(str(r[i])) for r in rows) for i in range(len(rows[0]))]
    for r in rows:
        print(" | ".join(str(c).rjust(widths[i]) for i, c in enumerate(r)))
    print(f"\nSaved: {out_csv}")
    return rows


if __name__ == "__main__":
    run_benchmarks()
