#!/usr/bin/env python3
"""
Visualisasi untuk presentasi Ujian CPMK-2.
Menghasilkan plot yang bisa digunakan di slide presentasi.
Menjalankan sim_fuzzy_spk.py untuk mendapatkan data.

Jalankan: python3 viz_presentasi.py
Output: plot_*.pdf di folder yang sama
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from sim_fuzzy_spk import mamdani_cog, DATA_MAHASISWA

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm

# ── Konfigurasi ──────────────────────────────────────────────────────
OUTDIR = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({
    "font.size": 11,
    "font.family": "serif",
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "figure.dpi": 150,
})

# ═════════════════════════════════════════════════════════════════════
# Plot 1: Surface Plot NK(ip, minat)
# ═════════════════════════════════════════════════════════════════════
def plot_surface():
    ip_vals = np.linspace(0, 4, 80)
    minat_vals = np.linspace(0, 4, 80)
    IP, MINAT = np.meshgrid(ip_vals, minat_vals)
    NK = np.zeros_like(IP)

    for i in range(IP.shape[0]):
        for j in range(IP.shape[1]):
            res = mamdani_cog(IP[i, j], MINAT[i, j])
            NK[i, j] = res["cog"]

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(IP, MINAT, NK, cmap=cm.RdYlGn, alpha=0.85,
                           edgecolor="none", antialiased=True)

    ax.set_xlabel("IPK")
    ax.set_ylabel("Minat")
    ax.set_zlabel("Nilai Kelayakan (NK)")
    ax.set_title("Surface Plot: Nilai Kelayakan berdasarkan IPK dan Minat")

    # Tandai data target #20
    for kbk, color, marker in [("ITP", "blue", "o"), ("RPLD", "red", "s"), ("SKJK", "green", "^")]:
        idx = {"ITP": 0, "RPLD": 1, "SKJK": 2}[kbk]
        ip20 = DATA_MAHASISWA[-1][1 + idx * 2]
        m20 = DATA_MAHASISWA[-1][2 + idx * 2]
        nk20 = mamdani_cog(ip20, m20)["cog"]
        ax.scatter([ip20], [m20], [nk20], color=color, s=120, marker=marker,
                   edgecolors="black", linewidths=1, zorder=5, label=f"{kbk}: NK={nk20:.1f}")

    ax.legend(loc="upper left", fontsize=9)
    fig.colorbar(surf, ax=ax, shrink=0.5, label="NK")
    ax.view_init(elev=25, azim=225)

    path = os.path.join(OUTDIR, "plot_surface_nk.pdf")
    fig.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


# ═════════════════════════════════════════════════════════════════════
# Plot 2: Decision Boundary (2D heatmap)
# ═════════════════════════════════════════════════════════════════════
def plot_decision_boundary():
    ip_vals = np.linspace(0, 4, 200)
    minat_vals = np.linspace(0, 4, 200)
    IP, MINAT = np.meshgrid(ip_vals, minat_vals)
    NK = np.zeros_like(IP)

    for i in range(IP.shape[0]):
        for j in range(IP.shape[1]):
            NK[i, j] = mamdani_cog(IP[i, j], MINAT[i, j])["cog"]

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.contourf(IP, MINAT, NK, levels=20, cmap=cm.RdYlGn)
    ax.contour(IP, MINAT, NK, levels=[50, 75], colors=["black"], linewidths=1.5,
               linestyles="dashed")
    ax.clabel(ax.contour(IP, MINAT, NK, levels=[50, 75], colors=["black"],
                         linewidths=1.5, linestyles="dashed"), fmt="NK=%.0f", fontsize=9)

    # Tandai data target #20
    for kbk, color, marker in [("ITP", "blue", "o"), ("RPLD", "red", "s"), ("SKJK", "green", "^")]:
        idx = {"ITP": 0, "RPLD": 1, "SKJK": 2}[kbk]
        ip20 = DATA_MAHASISWA[-1][1 + idx * 2]
        m20 = DATA_MAHASISWA[-1][2 + idx * 2]
        nk20 = mamdani_cog(ip20, m20)["cog"]
        ax.scatter(ip20, m20, color=color, s=150, marker=marker,
                   edgecolors="black", linewidths=1.5, zorder=5,
                   label=f"{kbk}: ({ip20}, {m20}) → NK={nk20:.1f}")

    ax.set_xlabel("IPK")
    ax.set_ylabel("Minat")
    ax.set_title("Decision Boundary: Nilai Kelayakan (NK)")
    ax.legend(loc="upper left", fontsize=9)
    fig.colorbar(im, ax=ax, label="Nilai Kelayakan")

    path = os.path.join(OUTDIR, "plot_decision_boundary.pdf")
    fig.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


# ═════════════════════════════════════════════════════════════════════
# Plot 3: Bar chart NK semua 20 data
# ═════════════════════════════════════════════════════════════════════
def plot_bar_all():
    from sim_fuzzy_spk import rekomendasi_kbks

    nos, nk_itp, nk_rpld, nk_skjk, rek_list, pilihan_list = [], [], [], [], [], []

    for row in DATA_MAHASISWA:
        no, ip_i, m_i, ip_r, m_r, ip_s, m_s, pilihan = row
        res = rekomendasi_kbks(ip_i, m_i, ip_r, m_r, ip_s, m_s)

        nos.append(no)
        nk_itp.append(res["nk"]["ITP"])
        nk_rpld.append(res["nk"]["RPLD"])
        nk_skjk.append(res["nk"]["SKJK"])
        rek_list.append(res["rekomendasi"])
        pilihan_list.append(pilihan)

    x = np.arange(len(nos))
    width = 0.25

    fig, ax = plt.subplots(figsize=(14, 5))
    bars1 = ax.bar(x - width, nk_itp, width, label="ITP", color="royalblue", alpha=0.8)
    bars2 = ax.bar(x, nk_rpld, width, label="RPLD", color="crimson", alpha=0.8)
    bars3 = ax.bar(x + width, nk_skjk, width, label="SKJK", color="forestgreen", alpha=0.8)

    # Tandai rekomendasi dengan bintang
    for i, rek in enumerate(rek_list):
        offset_map = {"ITP": -width, "RPLD": 0, "SKJK": width}
        nk_map = {"ITP": nk_itp, "RPLD": nk_rpld, "SKJK": nk_skjk}
        ax.annotate("*", (x[i] + offset_map[rek], nk_map[rek][i] + 2),
                    ha="center", fontsize=14, color="black", fontweight="bold")

    # Tandai data #20
    ax.axvline(x=19, color="gold", linewidth=2, linestyle="--", alpha=0.7)
    ax.annotate("TARGET\n#20 → RPLD", (19, 85), ha="center", fontsize=9,
                color="darkred", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))

    ax.set_xlabel("Nomor Mahasiswa")
    ax.set_ylabel("Nilai Kelayakan (NK)")
    ax.set_title("Hasil Rekomendasi SPK Fuzzy — 20 Mahasiswa (★ = Rekomendasi)")
    ax.set_xticks(x)
    ax.set_xticklabels(nos)
    ax.set_ylim(0, 100)
    ax.legend(loc="upper left")
    ax.grid(axis="y", alpha=0.3)

    path = os.path.join(OUTDIR, "plot_bar_all.pdf")
    fig.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


# ═════════════════════════════════════════════════════════════════════
# Plot 4: Bar chart detail data target #20
# ═════════════════════════════════════════════════════════════════════
def plot_bar_target():
    kbks = ["ITP", "RPLD", "SKJK"]
    nks = []
    for idx in range(3):
        ip20 = DATA_MAHASISWA[-1][1 + idx * 2]
        m20 = DATA_MAHASISWA[-1][2 + idx * 2]
        nks.append(mamdani_cog(ip20, m20)["cog"])

    colors = ["royalblue" if k != "RPLD" else "crimson" for k in kbks]
    edge_colors = ["navy" if k != "RPLD" else "darkred" for k in kbks]

    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.bar(kbks, nks, color=colors, edgecolor=edge_colors, linewidth=2, width=0.5)

    for bar, nk in zip(bars, nks):
        ax.text(bar.get_x() + bar.get_width() / 2, nk + 2,
                f"{nk:.2f}", ha="center", fontweight="bold", fontsize=12)

    ax.axhline(y=max(nks), color="gold", linewidth=1.5, linestyle="--", alpha=0.7)
    ax.set_ylabel("Nilai Kelayakan (NK)")
    ax.set_title("Data Target #20 — Perbandingan NK")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", alpha=0.3)

    # Annotate winner
    ax.annotate("REKOMENDASI → RPLD", xy=(1, 75), xytext=(1.7, 90),
                fontsize=11, fontweight="bold", color="darkred",
                arrowprops=dict(arrowstyle="->", color="darkred", lw=2),
                bbox=dict(boxstyle="round,pad=0.4", facecolor="lightyellow", edgecolor="darkred"))

    path = os.path.join(OUTDIR, "plot_bar_target.pdf")
    fig.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


# ═════════════════════════════════════════════════════════════════════
# Plot 5: MF curves dengan input markers
# ═════════════════════════════════════════════════════════════════════
def plot_mf_detail():
    from sim_fuzzy_spk import MF_IP, MF_MINAT, tri

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    # --- IP MF ---
    ax = axes[0]
    x = np.linspace(0, 4, 400)
    for name, (a, b, c) in MF_IP.items():
        y = [tri(xi, a, b, c) for xi in x]
        ax.plot(x, y, linewidth=2, label=name.capitalize())

    # Data #20 markers
    for kbk, idx, color in [("ITP", 0, "blue"), ("RPLD", 1, "red"), ("SKJK", 2, "green")]:
        ip_val = DATA_MAHASISWA[-1][1 + idx * 2]
        ax.axvline(ip_val, color=color, linestyle="--", alpha=0.6, linewidth=1.5)
        ax.plot(ip_val, tri(ip_val, 3, 3.5, 4), "v", color=color, markersize=10,
                markeredgecolor="black", markeredgewidth=1, label=f"{kbk}: IP={ip_val}")

    ax.set_xlabel("IPK")
    ax.set_ylabel("μ")
    ax.set_title("Membership Function — IP")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # --- Minat MF ---
    ax = axes[1]
    for name, (a, b, c) in MF_MINAT.items():
        y = [tri(xi, a, b, c) for xi in x]
        ax.plot(x, y, linewidth=2, label=name.replace("_", " ").title())

    for kbk, idx, color in [("ITP", 0, "blue"), ("RPLD", 1, "red"), ("SKJK", 2, "green")]:
        m_val = DATA_MAHASISWA[-1][2 + idx * 2]
        # Find the max μ at this value
        mu_max = max(tri(m_val, *v) for v in MF_MINAT.values())
        ax.axvline(m_val, color=color, linestyle="--", alpha=0.6, linewidth=1.5)
        ax.plot(m_val, mu_max, "v", color=color, markersize=10,
                markeredgecolor="black", markeredgewidth=1, label=f"{kbk}: M={m_val}")

    ax.set_xlabel("Minat")
    ax.set_ylabel("μ")
    ax.set_title("Membership Function — Minat")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    fig.suptitle("Fuzzifikasi Data Target #20", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    path = os.path.join(OUTDIR, "plot_mf_detail.pdf")
    fig.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


# ═════════════════════════════════════════════════════════════════════
# Main
# ═════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating visualization plots...")
    plot_mf_detail()        # Fast
    plot_bar_target()        # Fast
    plot_bar_all()           # Fast (reuses simulation)
    print("\nGenerating surface plot (this may take a moment)...")
    plot_surface()
    print("Generating decision boundary...")
    plot_decision_boundary()
    print("\nAll plots generated!")
