"""
Neutrosophic vs Affine Arithmetic — Reference Implementation.

Companion code for:
  Leyva Vazquez, M. Y. & Smarandache, F. (2026).
  Neutrosophic Interval-Indeterminate Numbers of the Form a+bI:
  A Comparative Analysis with Interval and Affine Arithmetic, with
  Multi-Source and Hesitant Extensions.

Modules:
  interval        — classical interval arithmetic [a,b]
  affine          — affine forms x0 + sum xi*ei
  neutrosophic    — classical a + bI
  msnn            — multi-source neutrosophic a + sum bi*Ii
  hesitant        — hesitant neutrosophic a + b*H(I)
  score           — score / ranking utilities
"""
from .interval import Interval
from .affine import Affine, reset_noise_counter, new_noise_id
from .neutrosophic import Neutrosophic
from .msnn import MSNN
from .hesitant import HesitantNeutrosophic

__all__ = [
    "Interval", "Affine", "Neutrosophic", "MSNN", "HesitantNeutrosophic",
    "reset_noise_counter", "new_noise_id",
]
__version__ = "1.0.0"
