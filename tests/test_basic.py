"""Sanity tests for all four formalisms."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib import Interval, Affine, Neutrosophic, MSNN, HesitantNeutrosophic, reset_noise_counter
from lib.msnn import reset_source_counter

def almost(a, b, tol=1e-6):
    return abs(a - b) < tol


def test_dependency_problem():
    """Canonical test: N - N should be 0 (affine/neutrosophic) or spurious (interval)."""
    # Interval
    x = Interval(100, 105)
    r = x - x
    assert r.range() == (-5.0, 5.0), f"Interval N-N should be spurious [-5, 5], got {r.range()}"

    # Affine
    reset_noise_counter()
    x_hat = Affine.from_interval(100, 105)
    r = x_hat - x_hat
    assert almost(r.range()[0], 0) and almost(r.range()[1], 0), f"Affine N-N should be 0, got {r.range()}"

    # Neutrosophic
    N = Neutrosophic.from_interval(100, 105)
    r = N - N
    assert almost(r.a, 0) and almost(r.b, 0), f"Neutrosophic N-N should be 0, got {r}"

    # MSNN
    reset_source_counter()
    Nm = MSNN.from_interval(100, 105)
    r = Nm - Nm
    assert almost(r.range()[0], 0) and almost(r.range()[1], 0), f"MSNN N-N should be 0, got {r.range()}"

    print("[PASS] test_dependency_problem")


def test_theorem1_range_equivalence_1d():
    """
    Theorem 1: a+bI and affine arithmetic are range-equivalent in 1D.
    Check on several expressions with a single uncertain variable.
    """
    expressions = [
        ("x",       lambda x: x,                    "identity"),
        ("2x+3",    lambda x: 2 * x + 3,             "linear"),
        ("x-x",     lambda x: x - x,                 "self-cancel"),
        ("x+x-2x",  lambda x: x + x - 2 * x,         "affine combo"),
        ("3x-3x+7", lambda x: 3 * x - 3 * x + 7,     "constant after cancel"),
    ]

    for name, f, desc in expressions:
        # Affine
        reset_noise_counter()
        x_hat = Affine.from_interval(10, 20)
        ra = f(x_hat).range()
        # Neutrosophic
        N = Neutrosophic.from_interval(10, 20)
        rn = f(N).range()
        # MSNN
        reset_source_counter()
        Nm = MSNN.from_interval(10, 20)
        rm = f(Nm).range()

        assert almost(ra[0], rn[0]) and almost(ra[1], rn[1]), \
            f"Theorem 1 fails for {name} ({desc}): affine={ra}, N={rn}"
        assert almost(ra[0], rm[0]) and almost(ra[1], rm[1]), \
            f"Theorem 1 fails for {name} ({desc}): affine={ra}, MSNN={rm}"

    print("[PASS] test_theorem1_range_equivalence_1d (5 expressions)")


def test_theorem2_range_equivalence_nd():
    """
    Theorem 2: MSNN and affine arithmetic are range-equivalent in N-D.
    Check on expressions with 2 independent sources.
    """
    # 2 sources
    reset_noise_counter()
    reset_source_counter()

    a_hat = Affine.from_interval(10, 20)
    b_hat = Affine.from_interval(5, 10)
    Ma = MSNN.from_interval(10, 20)
    Mb = MSNN.from_interval(5, 10)

    # Affine expressions (only +/- and scalar multiplication)
    expressions = [
        ("a+b",     lambda a, b: a + b),
        ("a-b",     lambda a, b: a - b),
        ("a+b-a",   lambda a, b: a + b - a),  # should cancel 'a' exactly
        ("2a+3b",   lambda a, b: 2 * a + 3 * b),
        ("5a-4b+7", lambda a, b: 5 * a - 4 * b + 7),
    ]

    for name, f in expressions:
        ra = f(a_hat, b_hat).range()
        rm = f(Ma, Mb).range()
        assert almost(ra[0], rm[0]) and almost(ra[1], rm[1]), \
            f"Theorem 2 fails for {name}: affine={ra}, MSNN={rm}"

    print("[PASS] test_theorem2_range_equivalence_nd (5 expressions, 2 sources)")


def test_interval_dependency_overestimation():
    """Quantify how much interval arithmetic overestimates vs. affine/MSNN."""
    # Expression with 3 occurrences of x: f(x) = (x-10)*(x+10) where x in [1, 3]
    # Exact: x^2 - 100, range on [1,3] = [1-100, 9-100] = [-99, -91]. Width 8.
    # Interval arithmetic overestimates.
    x_i = Interval(1, 3)
    f_i = (x_i - Interval(10)) * (x_i + Interval(10))
    print(f"  (x-10)*(x+10) with x in [1,3]:")
    print(f"    Exact range:    [-99, -91]  (width 8)")
    print(f"    Interval:       {f_i}  (width {f_i.width:.2f})")

    reset_noise_counter()
    x_a = Affine.from_interval(1, 3)
    f_a = (x_a - 10) * (x_a + 10)
    print(f"    Affine:         [{f_a.range()[0]:.2f}, {f_a.range()[1]:.2f}]  (width {f_a.total_deviation()*2:.2f})")

    reset_source_counter()
    x_m = MSNN.from_interval(1, 3)
    f_m = (x_m - 10) * (x_m + 10)
    print(f"    MSNN:           [{f_m.range()[0]:.2f}, {f_m.range()[1]:.2f}]")


def test_hesitant_cardiologists():
    """Reproduce the cardiologist example from Section 5.3."""
    # Baseline 120 mmHg; max caffeine-induced increase 15 mmHg.
    # 3 experts report:
    #   A: 0-10 mmHg  -> I in [0, 0.67]
    #   B: 5-15 mmHg  -> I in [0.33, 1.0]
    #   C: 0-8 mmHg   -> I in [0, 0.53]
    N_H = HesitantNeutrosophic(120, 15, [(0.0, 0.67), (0.33, 1.0), (0.0, 0.53)])

    print(f"  Hesitant BP assessment: {N_H}")
    print(f"    Envelope range: {N_H.range()}")
    print(f"    Per-expert ranges: {N_H.expert_ranges()}")
    print(f"    Score (mean_mid): {N_H.score('mean_mid'):.3f}")
    print(f"    Score (median_mid): {N_H.score('median_mid'):.3f}")
    print(f"    Score (min_lo, pessimistic): {N_H.score('min_lo'):.3f}")
    print(f"    Score (max_hi, optimistic): {N_H.score('max_hi'):.3f}")


def run_all():
    print("=" * 64)
    print("Running sanity tests for neutrosophic / affine / interval / MSNN / hesitant")
    print("=" * 64)
    test_dependency_problem()
    test_theorem1_range_equivalence_1d()
    test_theorem2_range_equivalence_nd()
    print()
    print("Interval overestimation demo:")
    test_interval_dependency_overestimation()
    print()
    print("Hesitant neutrosophic demo:")
    test_hesitant_cardiologists()
    print()
    print("All tests passed.")


if __name__ == "__main__":
    run_all()
