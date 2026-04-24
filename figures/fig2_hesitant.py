"""
Figure 2: Hesitant Neutrosophic representation of the 3 cardiologists.
Shows how hesitant structure preserves expert-level disagreement, vs the
collapsed envelope that interval / affine / classical neutrosophic would yield.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lib import HesitantNeutrosophic

OUT = os.path.join(os.path.dirname(__file__), "fig2_hesitant.png")

# 3 experts, baseline 120, b=15
N_H = HesitantNeutrosophic(120, 15, [(0.0, 0.67), (0.33, 1.0), (0.0, 0.53)])
expert_names = ["Cardiologist A", "Cardiologist B", "Cardiologist C"]
expert_ranges = N_H.expert_ranges()
colors = ['#4472C4', '#70AD47', '#ED7D31']

fig, axes = plt.subplots(2, 1, figsize=(11, 5.5))
fig.suptitle("Expert BP Assessment after Caffeine: Hesitant Neutrosophic vs Collapsed Envelope",
             fontsize=13, fontweight='bold')

# ---- top: collapsed envelope (what interval / affine / a+bI would see) ----
ax = axes[0]
ax.set_title("(a) Interval / Affine / Classical $a+bI$: collapsed envelope  →  [120, 135] mmHg, disagreement lost",
             fontsize=10, color='#C00000')
env_lo, env_hi = N_H.range()
ax.barh([0], [env_hi - env_lo], left=env_lo, color='#F4B084', edgecolor='#C00000', linewidth=1.5)
ax.set_yticks([0])
ax.set_yticklabels(['Envelope'])
ax.set_xlim(118, 137)
ax.set_xlabel("Systolic BP (mmHg)", fontsize=9)
ax.grid(alpha=0.3, axis='x')
ax.axvline(120, color='gray', linestyle=':', alpha=0.7, label='baseline = 120')
ax.legend(loc='upper right', fontsize=8)

# ---- bottom: hesitant structure preserves each expert ----
ax = axes[1]
ax.set_title(f"(b) Hesitant Neutrosophic $N_H = 120 + 15 \\cdot H(I)$  →  per-expert structure preserved",
             fontsize=10, color='#00B050')
for i, ((lo, hi), name, color) in enumerate(zip(expert_ranges, expert_names, colors)):
    ax.barh([i], [hi - lo], left=lo, color=color, edgecolor='black', linewidth=1, alpha=0.8)
    ax.text((lo + hi) / 2, i, f"[{lo:.1f}, {hi:.1f}]", ha='center', va='center',
            fontsize=9, fontweight='bold', color='white')
ax.set_yticks(range(len(expert_names)))
ax.set_yticklabels(expert_names)
ax.set_xlim(118, 137)
ax.set_xlabel("Systolic BP (mmHg)", fontsize=9)
ax.grid(alpha=0.3, axis='x')
ax.axvline(120, color='gray', linestyle=':', alpha=0.7)
ax.axvline(N_H.score('mean_mid'), color='red', linestyle='--', linewidth=1.5,
           label=f'score (mean-mid) = {N_H.score("mean_mid"):.2f}')
ax.legend(loc='upper right', fontsize=8)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(OUT, dpi=150, bbox_inches='tight')
print(f"Saved: {OUT}")
