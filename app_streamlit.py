#!/usr/bin/env python3
"""
Streamlit Web App — SPK Pemilihan KBK (Fuzzy Mamdani)
Ujian CPMK-2: Kecerdasan Buatan (MTE25112)

Jalankan: streamlit run app_streamlit.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from sim_fuzzy_spk import mamdani_cog, rekomendasi_kbks, DATA_MAHASISWA, MF_IP, MF_MINAT, MF_NK, RULES, tri

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st

# ═════════════════════════════════════════════════════════════════════
# Page config
# ═════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="SPK Fuzzy — Pemilihan KBK", layout="wide",
                   page_icon="🎯")

st.title("🎯 SPK Pemilihan KBK")
st.caption("Fuzzy Mamdani | Ujian CPMK-2 | RIYADI H2A025002")

# ═════════════════════════════════════════════════════════════════════
# Sidebar: Input
# ═════════════════════════════════════════════════════════════════════
st.sidebar.header("📥 Input")

mode = st.sidebar.radio("Mode:", ["Data Kustom", "Data Survei (#1-20)"], index=0)

if mode == "Data Kustom":
    st.sidebar.markdown("**Nilai per KBK:**")
    ip_itp = st.sidebar.slider("ITP — IPK", 0.0, 4.0, 3.40, 0.01)
    m_itp  = st.sidebar.slider("ITP — Minat", 0.0, 4.0, 2.60, 0.01)
    ip_rpld = st.sidebar.slider("RPLD — IPK", 0.0, 4.0, 3.52, 0.01)
    m_rpld  = st.sidebar.slider("RPLD — Minat", 0.0, 4.0, 2.80, 0.01)
    ip_skjk = st.sidebar.slider("SKJK — IPK", 0.0, 4.0, 3.65, 0.01)
    m_skjk  = st.sidebar.slider("SKJK — Minat", 0.0, 4.0, 1.50, 0.01)
    res = rekomendasi_kbks(ip_itp, m_itp, ip_rpld, m_rpld, ip_skjk, m_skjk)
    target_label = None
else:
    no = st.sidebar.selectbox("Pilih mahasiswa:", list(range(1, 21)), index=19)
    row = DATA_MAHASISWA[no - 1]
    ip_itp, m_itp = row[1], row[2]
    ip_rpld, m_rpld = row[3], row[4]
    ip_skjk, m_skjk = row[5], row[6]
    target_label = row[7]
    res = rekomendasi_kbks(ip_itp, m_itp, ip_rpld, m_rpld, ip_skjk, m_skjk)

# ═════════════════════════════════════════════════════════════════════
# Main: Metrics row
# ═════════════════════════════════════════════════════════════════════
nk = res["nk"]
rek = res["rekomendasi"]

c1, c2, c3, c4 = st.columns(4)

def show_nk(col, kbk, value, is_winner):
    with col:
        icon = "🏆" if is_winner else "📊"
        st.metric(f"{icon} {kbk}", f"{value:.2f}",
                  delta="REKOMENDASI" if is_winner else None,
                  delta_color="normal" if is_winner else "off")

show_nk(c1, "ITP", nk["ITP"], rek == "ITP")
show_nk(c2, "RPLD", nk["RPLD"], rek == "RPLD")
show_nk(c3, "SKJK", nk["SKJK"], rek == "SKJK")
with c4:
    st.metric("🏆 Rekomendasi", rek)

if target_label and target_label != "?":
    match = rek == target_label
    if match:
        st.success(f"✅ Sesuai pilihan: **{target_label}**")
    else:
        st.error(f"❌ Tidak sesuai! Pilihan: **{target_label}**, sistem: **{rek}**")
elif target_label == "?":
    st.info(f"📋 Target #20 → Sistem merekomendasikan: **{rek}**")

# ═════════════════════════════════════════════════════════════════════
# Tabs (3 tabs instead of 4)
# ═════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["📊 Perhitungan", "📈 Visualisasi", "📋 Data Survei"])

# ── Tab 1: Compact calculation table ────────────────────────────────
with tab1:
    rows = []
    for kbk in ["ITP", "RPLD", "SKJK"]:
        d = res["detail"][kbk]
        ip_val = d["input"]["ip"]
        m_val = d["input"]["minat"]

        # Active MFs with values
        mu_ip_items = [(k, v) for k, v in d["fuzzifikasi"]["ip"].items() if v > 0]
        mu_m_items = [(k, v) for k, v in d["fuzzifikasi"]["minat"].items() if v > 0]
        mu_ip_str = ", ".join(f"μ_{k}={v:.2f}" for k, v in mu_ip_items)
        mu_m_str = ", ".join(f"μ_{k}={v:.2f}" for k, v in mu_m_items)

        # Active rules
        active_rules = []
        for r in d["aturan"]:
            if r["aktif"]:
                active_rules.append(f"{r['label']}(α={r['alpha']:.2f}→{r['konsekuen']})")
        rules_str = " + ".join(active_rules)

        is_w = "★" if kbk == rek else ""
        rows.append({
            "": is_w,
            "KBK": kbk,
            "IP": ip_val,
            "Minat": m_val,
            "μ IP aktif": mu_ip_str,
            "μ Minat aktif": mu_m_str,
            "Rules": rules_str,
            "NK (COG)": f"{d['cog']:.2f}",
        })

    st.dataframe(rows, use_container_width=True, hide_index=True, height=130)

    with st.expander("Detail per KBK"):
        for kbk in ["ITP", "RPLD", "SKJK"]:
            d = res["detail"][kbk]
            ip_val = d["input"]["ip"]
            m_val = d["input"]["minat"]
            icon = "🏆" if kbk == rek else "📊"
            st.markdown(f"**{icon} {kbk}** (IP={ip_val}, Minat={m_val} → NK={d['cog']:.2f})")

            lc, rc = st.columns(2)
            with lc:
                for k, v in d["fuzzifikasi"]["ip"].items():
                    if v > 0:
                        st.write(f"  μ_{k}({ip_val}) = {v:.4f}")
            with rc:
                for k, v in d["fuzzifikasi"]["minat"].items():
                    if v > 0:
                        st.write(f"  μ_{k}({m_val}) = {v:.4f}")

            for r in d["aturan"]:
                if r["aktif"]:
                    st.write(f"  {r['label']}: {r['ip_key']}×{r['minat_key']} → {r['konsekuen']}, "
                             f"α = min({r['mu_ip']:.4f}, {r['mu_minat']:.4f}) = **{r['alpha']:.4f}**")
            st.divider()

# ── Tab 2: 2×2 chart grid ──────────────────────────────────────────
with tab2:
    # Row 1: MF plots
    c_left, c_right = st.columns(2)

    with c_left:
        fig, ax = plt.subplots(figsize=(5, 2.8))
        x = np.linspace(0, 4, 300)
        colors_ip = {"kecil": "blue", "cukup": "orange", "bagus": "green"}
        for name, (a, b, c) in MF_IP.items():
            y = [tri(xi, a, b, c) for xi in x]
            ax.plot(x, y, linewidth=2, label=name.capitalize(), color=colors_ip[name])
        for kbk, idx, color in [("ITP", 0, "royalblue"), ("RPLD", 1, "crimson"), ("SKJK", 2, "forestgreen")]:
            ip_v = [ip_itp, ip_rpld, ip_skjk][idx]
            mu_v = max(tri(ip_v, *v) for v in MF_IP.values())
            ax.axvline(ip_v, color=color, linestyle="--", alpha=0.4)
            ax.plot(ip_v, mu_v, "o", color=color, markersize=6, label=f"{kbk}: {ip_v}")
        ax.set_xlabel("IPK"); ax.set_ylabel("μ"); ax.legend(fontsize=7, loc="upper left"); ax.grid(alpha=0.3)
        ax.set_title("MF — IPK")
        st.pyplot(fig); plt.close()

    with c_right:
        fig, ax = plt.subplots(figsize=(5, 2.8))
        colors_m = {"tidak_suka": "blue", "suka": "orange", "sangat_suka": "green"}
        for name, (a, b, c) in MF_MINAT.items():
            y = [tri(xi, a, b, c) for xi in x]
            ax.plot(x, y, linewidth=2, label=name.replace("_", " ").title(), color=colors_m[name])
        for kbk, idx, color in [("ITP", 0, "royalblue"), ("RPLD", 1, "crimson"), ("SKJK", 2, "forestgreen")]:
            m_v = [m_itp, m_rpld, m_skjk][idx]
            mu_v = max(tri(m_v, *v) for v in MF_MINAT.values())
            ax.axvline(m_v, color=color, linestyle="--", alpha=0.4)
            ax.plot(m_v, mu_v, "o", color=color, markersize=6, label=f"{kbk}: {m_v}")
        ax.set_xlabel("Minat"); ax.set_ylabel("μ"); ax.legend(fontsize=7, loc="upper left"); ax.grid(alpha=0.3)
        ax.set_title("MF — Minat")
        st.pyplot(fig); plt.close()

    # Row 2: Bar chart + Decision Boundary
    c_bar, c_db = st.columns(2)

    with c_bar:
        fig, ax = plt.subplots(figsize=(5, 2.8))
        kbks = ["ITP", "RPLD", "SKJK"]
        nks = [nk[k] for k in kbks]
        bar_colors = ["forestgreen" if k == rek else "lightgray" for k in kbks]
        bars = ax.bar(kbks, nks, color=bar_colors, edgecolor="black", width=0.5)
        for bar, val in zip(bars, nks):
            ax.text(bar.get_x() + bar.get_width()/2, val + 2, f"{val:.1f}",
                    ha="center", fontweight="bold", fontsize=10)
        ax.set_ylabel("NK"); ax.set_ylim(0, 100); ax.grid(axis="y", alpha=0.3)
        ax.set_title("Perbandingan NK")
        st.pyplot(fig); plt.close()

    with c_db:
        progress = st.progress(0, text="Menghitung...")

        n_pts = 40
        ip_vals = np.linspace(0, 4, n_pts)
        minat_vals = np.linspace(0, 4, n_pts)
        IP, MINAT = np.meshgrid(ip_vals, minat_vals)
        NK_MAP = np.zeros_like(IP)

        for i in range(n_pts):
            for j in range(n_pts):
                NK_MAP[i, j] = mamdani_cog(IP[i, j], MINAT[i, j])["cog"]
            progress.progress(int((i + 1) / n_pts * 100),
                              text=f"Menghitung... {i+1}/{n_pts}")

        fig, ax = plt.subplots(figsize=(5, 2.8))
        im = ax.contourf(IP, MINAT, NK_MAP, levels=20, cmap="RdYlGn")
        ax.contour(IP, MINAT, NK_MAP, levels=[50, 75], colors=["black"],
                   linewidths=1, linestyles="dashed")
        for kbk, idx, color, marker in [("ITP", 0, "blue", "o"), ("RPLD", 1, "red", "s"), ("SKJK", 2, "green", "^")]:
            ip_v = [ip_itp, ip_rpld, ip_skjk][idx]
            m_v = [m_itp, m_rpld, m_skjk][idx]
            ax.scatter(ip_v, m_v, color=color, s=80, marker=marker,
                       edgecolors="black", linewidths=1, zorder=5, label=kbk)
        ax.set_xlabel("IPK"); ax.set_ylabel("Minat"); ax.legend(fontsize=7, loc="upper left")
        ax.set_title("Decision Boundary")
        fig.colorbar(im, ax=ax, shrink=0.8, label="NK")
        st.pyplot(fig); plt.close()
        progress.empty()

    st.caption(
        "🗺 Decision boundary: merah = NK rendah, hijau = NK tinggi. "
        "NK tinggi hanya tercapai jika IPK dan Minat keduanya memadai. "
        "Area kanan-bawah tetap rendah akibat Rule R7 (IP bagus × Minat rendah → Sedang)."
    )

# ── Tab 3: Data Survei ──────────────────────────────────────────────
with tab3:
    rows = []
    benar = 0
    for row in DATA_MAHASISWA:
        no, ip_i, m_i, ip_r, m_r, ip_s, m_s, pilihan = row
        r = rekomendasi_kbks(ip_i, m_i, ip_r, m_r, ip_s, m_s)
        rek_i = r["rekomendasi"]
        status = ""
        if pilihan != "?":
            status = "✅" if rek_i == pilihan else "❌"
            if rek_i == pilihan:
                benar += 1
        else:
            status = "🎯 TARGET"
        rows.append({
            "No": no, "Pilihan": pilihan,
            "NK ITP": f"{r['nk']['ITP']:.1f}",
            "NK RPLD": f"{r['nk']['RPLD']:.1f}",
            "NK SKJK": f"{r['nk']['SKJK']:.1f}",
            "Rek": rek_i, "": status,
        })

    c_tbl, c_met = st.columns([4, 1])
    with c_tbl:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    with c_met:
        st.metric("Akurasi", f"{benar}/19", f"{benar/19*100:.0f}%")
