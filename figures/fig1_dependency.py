"""
Figure 1: The dependency problem — visualization.
Shows how three formalisms treat N - N for N = [100, 105].
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from lib import Interval, Affine, Neutrosophic, MSNN, reset_noise_counter
from lib.msnn import reset_source_counter

OUT = os.path.join(os.path.dirname(__file__), "fig1_dependency.png")

fig, axes = plt.subplots(3, 1, figsize=(10, 5.5), sharex=False)
fig.suptitle("The Dependency Problem: computing $N - N$ with $N = [100, 105]$",
             fontsize=13, fontweight='bold')

# ---- 1. Interval ----
ax = axes[0]
ax.set_title("(a) Classical Interval: $[100,105] - [100,105] = [-5, +5]$  →  spurious width 10",
             fontsize=10, color='#C00000')
ax.axhline(0, color='gray', linewidth=0.8)
ax.add_patch(patches.FancyBboxPatch((-5, -0.3), 10, 0.6, boxstyle="round,pad=0.05",
                                      facecolor='#f28b82', edgecolor='#C00000', linewidth=2))
ax.plot(0, 0, 'ko', markersize=8, zorder=10)
ax.annotate('expected: 0', xy=(0, 0), xytext=(0.8, 0.5),
            arrowprops=dict(arrowstyle='->', color='black'), fontsize=9)
ax.set_xlim(-7, 7)
ax.set_yticks([])
ax.set_xlabel("result value", fontsize=9)
ax.grid(alpha=0.3)

# ---- 2. Affine ----
ax = axes[1]
reset_noise_counter()
x = Affine.from_interval(100, 105)
r = x - x
ax.set_title(f"(b) Affine Arithmetic: cancellation via shared $e_1$  →  result = 0 (exact)",
             fontsize=10, color='#00B050')
ax.axhline(0, color='gray', linewidth=0.8)
ax.plot(r.x0, 0, 'go', markersize=12, zorder=10)
ax.annotate(f'result = {r.x0}', xy=(r.x0, 0), xytext=(0.8, 0.5),
            arrowprops=dict(arrowstyle='->', color='black'), fontsize=9)
ax.set_xlim(-7, 7)
ax.set_yticks([])
ax.set_xlabel("result value", fontsize=9)
ax.grid(alpha=0.3)

# ---- 3. Neutrosophic ----
ax = axes[2]
N = Neutrosophic.from_interval(100, 105)
r = N - N
ax.set_title(f"(c) Neutrosophic $N = 100 + 5I$: symbolic $I$ cancels  →  result = 0 (exact)",
             fontsize=10, color='#00B050')
ax.axhline(0, color='gray', linewidth=0.8)
ax.plot(r.a, 0, 'bo', markersize=12, zorder=10)
ax.annotate(f'result = {r.a:.0f} + {r.b:.0f}I = 0', xy=(r.a, 0), xytext=(0.8, 0.5),
            arrowprops=dict(arrowstyle='->', color='black'), fontsize=9)
ax.set_xlim(-7, 7)
ax.set_yticks([])
ax.set_xlabel("result value", fontsize=9)
ax.grid(alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(OUT, dpi=150, bbox_inches='tight')
print(f"Saved: {OUT}")
