"""
Figure 4: Decision tree for choosing an uncertainty formalism.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

OUT = os.path.join(os.path.dirname(__file__), "fig4_decision.png")

fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

def box(x, y, w, h, text, color='#E7E6E6', edge='black'):
    rect = mpatches.FancyBboxPatch((x - w/2, y - h/2), w, h,
                                    boxstyle="round,pad=0.1",
                                    facecolor=color, edgecolor=edge, linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x, y, text, ha='center', va='center', fontsize=10, fontweight='bold')

def arrow(x1, y1, x2, y2, label=''):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', lw=1.4, color='#555'))
    if label:
        ax.text((x1 + x2) / 2 + 0.1, (y1 + y2) / 2, label, fontsize=9, style='italic',
                color='#333', bbox=dict(boxstyle="round,pad=0.2", facecolor='white', edgecolor='none'))

ax.set_title("Figure 4. Decision tree for choosing an uncertainty formalism",
             fontsize=14, fontweight='bold', pad=15)

# Root
box(5, 9.2, 3.8, 0.7, "Uncertain quantity?", color='#DEEBF7')

# Level 1
box(5, 7.9, 4.2, 0.7, "Expert disagreement / multiple\nranges from different sources?",
    color='#FFF2CC')

# Level 2 options
box(1.8, 6.2, 2.7, 0.9, "Hesitant\nNeutrosophic $N_H$", color='#C6EFCE', edge='#00B050')
box(5, 6.2, 4.2, 0.8, "Single range\n(one source or consensus)", color='#DEEBF7')

# Level 3 branches
box(5, 4.9, 4.6, 0.7, "Repeated variables or\nshared sources?", color='#FFF2CC')

box(2.0, 3.2, 2.6, 0.7, "Single occurrence,\nno sharing", color='#DEEBF7')
box(7.5, 3.2, 3.2, 0.7, "Shared sources\n(yes)", color='#DEEBF7')

# Level 4 final
box(1.8, 1.6, 2.6, 0.9, "Classical Interval\n[a, b]", color='#F4B084', edge='#ED7D31')
box(5.3, 1.6, 2.8, 0.9, "Qualitative / semantic\ntransparency critical?", color='#FFF2CC')

box(3.7, 0.1, 2.6, 0.7, "Neutrosophic\n$a + bI$ (1D)\n$a + \\sum b_i I_i$ (N-D)",
    color='#C6EFCE', edge='#00B050')
box(7.5, 0.1, 2.6, 0.7, "Affine Arithmetic\n$x_0 + \\sum x_i e_i$",
    color='#BDD7EE', edge='#4472C4')

# Arrows
arrow(5, 8.85, 5, 8.25)
arrow(5, 7.55, 3, 6.6, 'Yes')
arrow(5, 7.55, 5, 6.6, 'No')

arrow(5, 5.8, 5, 5.25)
arrow(5, 4.55, 2.5, 3.55, 'No')
arrow(5, 4.55, 7.2, 3.55, 'Yes')

arrow(2.0, 2.85, 2.0, 2.05)
arrow(7.5, 2.85, 5.8, 2.05)
arrow(7.5, 2.85, 7.5, 0.45, '')

arrow(5.3, 1.15, 3.9, 0.45, 'Yes')
arrow(5.3, 1.15, 7.1, 0.45, 'No')

# Legend
legend_elements = [
    mpatches.Patch(facecolor='#C6EFCE', edgecolor='#00B050', label='Neutrosophic family'),
    mpatches.Patch(facecolor='#BDD7EE', edgecolor='#4472C4', label='Affine family'),
    mpatches.Patch(facecolor='#F4B084', edgecolor='#ED7D31', label='Interval (classical)'),
    mpatches.Patch(facecolor='#FFF2CC', edgecolor='black', label='Decision'),
    mpatches.Patch(facecolor='#DEEBF7', edgecolor='black', label='Context'),
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=9,
          bbox_to_anchor=(0.98, 1.0))

plt.tight_layout()
plt.savefig(OUT, dpi=150, bbox_inches='tight')
print(f"Saved: {OUT}")
