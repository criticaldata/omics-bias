"""
Figure 0: PRISMA diagram of the scoping review.
Numbers as in the chapter proof (Oct 2026); the full-text exclusion box is split so the
four records removed after inclusion are visible (104 did not meet criteria, 4 removed).
Writes figures/main/png/fig0_prisma.png and figures/main/pdf/fig0_prisma.pdf.
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

W, H = 11.0, 12.6
fig = plt.figure(figsize=(W, H), dpi=200)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")

BLUE, YELLOW = "#A9C4E4", "#F5C342"
FS = 14

def box(x, y, w, h, text, fs=FS):
    ax.add_patch(Rectangle((x, y), w, h, fill=False, lw=1.3, ec="black"))
    ax.text(x + 0.2, y + h / 2, text, fontsize=fs, va="center", ha="left", linespacing=1.5)

def side(y, h, label):
    ax.add_patch(FancyBboxPatch((0.45, y), 0.6, h, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc=BLUE, ec=BLUE))
    ax.text(0.75, y + h / 2, label, fontsize=FS, rotation=90, va="center", ha="center", weight="bold")

def arrow(x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", lw=1.3, color="black", mutation_scale=18))

# header
ax.add_patch(FancyBboxPatch((1.45, 11.75), 9.3, 0.55, boxstyle="round,pad=0.02,rounding_size=0.12",
                            fc=YELLOW, ec=YELLOW))
ax.text(6.1, 12.02, "Identification of studies via databases and registers",
        fontsize=FS, ha="center", va="center", weight="bold")

LX, LW, RX, RW = 1.45, 4.1, 6.8, 3.95

# identification
side(8.9, 2.65, "Identification")
box(LX, 8.9, LW, 2.65, "Records identified from:\n     PubMed and Scopus (n = 552)\n     CNKI and Wanfang (n = 17)")
box(RX, 8.9, RW, 2.65, "Records removed $\\it{before}$\n$\\it{screening}$:\n     Duplicate records removed\n     (n = 173)")
arrow(LX + LW, 10.22, RX, 10.22)

# screening
side(2.25, 6.15, "Screening")
box(LX, 7.1, LW, 1.1, "Records screened\n(n = 396)")
box(RX, 7.1, RW, 1.1, "Records excluded (Abstract)\n(n = 142)")
arrow(LX + LW, 7.65, RX, 7.65)
arrow(LX + LW / 2, 8.9, LX + LW / 2, 8.2)

box(LX, 5.35, LW, 1.1, "Reports sought for retrieval\n(n = 254)")
box(RX, 5.35, RW, 1.1, "Reports not retrieved\n(n = 0)")
arrow(LX + LW, 5.9, RX, 5.9)
arrow(LX + LW / 2, 7.1, LX + LW / 2, 6.45)

box(LX, 3.6, LW, 1.1, "Reports assessed for eligibility\n(n = 254)")
box(RX, 2.3, RW, 2.4, "Reports excluded (Full Text)\n(n = 108)\n     Did not meet criteria (n = 104)\n     Removed after inclusion (n = 4)")
arrow(LX + LW, 4.15, RX, 4.15)
arrow(LX + LW / 2, 5.35, LX + LW / 2, 4.7)

# included
side(0.4, 1.55, "Included")
box(LX, 0.4, LW, 1.55, "Studies included in review\n(n = 146)")
arrow(LX + LW / 2, 3.6, LX + LW / 2, 1.95)

for sub, ext in (("png", "png"), ("pdf", "pdf")):
    out = ROOT / "figures" / "main" / sub / f"fig0_prisma.{ext}"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, facecolor="white")
    print(f"wrote {out}")
