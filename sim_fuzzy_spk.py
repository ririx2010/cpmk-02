#!/usr/bin/env python3
"""
Simulasi Sistem Pendukung Keputusan (SPK) Pemilihan KBK
menggunakan Fuzzy Inference System (FIS) Metode Mamdani.
Ujian CPMK-2 — Kecerdasan Buatan (MTE25112).

Input : IPK (0-4) × Minat (0-4)  →  Output: Nilai Kelayakan (NK, 0-100)
Metode: Mamdani (implikasi=min, agregasi=max, defuzzifikasi=COG)
"""

from __future__ import annotations
import numpy as np


# ═══════════════════════════════════════════════════════════════════════
# Fungsi Keanggotaan Segitiga
# ═══════════════════════════════════════════════════════════════════════

def tri(x: float, a: float, b: float, c: float) -> float:
    """MF segitiga skalar: puncak di b, kaki kiri [a,b], kaki kanan [b,c]."""
    if x <= a or x >= c:
        return 0.0
    if x < b:
        return (x - a) / (b - a)
    return (c - x) / (c - b)


def tri_array(y_arr: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    """MF segitiga vektorisasi untuk array numpy."""
    out = np.zeros_like(y_arr)
    mask_left = (y_arr > a) & (y_arr < b)
    mask_right = (y_arr >= b) & (y_arr < c)
    out[mask_left] = (y_arr[mask_left] - a) / (b - a)
    out[mask_right] = (c - y_arr[mask_right]) / (c - b)
    return out


# ═══════════════════════════════════════════════════════════════════════
# Parameter Membership Functions
# ═══════════════════════════════════════════════════════════════════════

# Variabel Input: IP (semesta 0-4)
MF_IP = {
    "kecil":  (0.0, 1.0, 2.0),
    "cukup":  (1.5, 2.5, 3.5),
    "bagus":  (3.0, 3.5, 4.0),
}

# Variabel Input: Minat (semesta 0-4)
MF_MINAT = {
    "tidak_suka":  (0.0, 1.5, 2.5),
    "suka":        (2.0, 3.0, 4.0),
    "sangat_suka": (3.0, 3.5, 4.0),
}

# Variabel Output: Nilai Kelayakan / NK (semesta 0-100)
MF_NK = {
    "rendah": (0.0, 25.0, 50.0),
    "sedang": (25.0, 50.0, 75.0),
    "tinggi": (50.0, 75.0, 100.0),
}


# ═══════════════════════════════════════════════════════════════════════
# 9 Fuzzy Rules
# Format: (label, ip_key, minat_key, nk_key)
# ═══════════════════════════════════════════════════════════════════════

RULES = [
    ("R1", "kecil",  "tidak_suka",  "rendah"),   # IP rendah, tidak suka → Rendah
    ("R2", "kecil",  "suka",        "rendah"),   # IP rendah, walau suka → Rendah
    ("R3", "kecil",  "sangat_suka", "sedang"),   # IP rendah, sangat suka → Sedang
    ("R4", "cukup",  "tidak_suka",  "rendah"),   # IP cukup, tidak suka → Rendah
    ("R5", "cukup",  "suka",        "sedang"),   # IP cukup, suka → Sedang
    ("R6", "cukup",  "sangat_suka", "tinggi"),   # IP cukup, sangat suka → Tinggi
    ("R7", "bagus",  "tidak_suka",  "sedang"),   # IP bagus, tidak suka → Sedang
    ("R8", "bagus",  "suka",        "tinggi"),   # IP bagus, suka → Tinggi
    ("R9", "bagus",  "sangat_suka", "tinggi"),   # IP bagus, sangat suka → Tinggi
]

RULE_JUSTIFICATIONS = {
    "R1": "IP rendah + tidak suka → jelas tidak layak",
    "R2": "IP rendah walau ada minat → syarat akademik belum terpenuhi",
    "R3": "IP rendah tapi sangat tertarik → peluang diberikan (Sedang)",
    "R4": "IP cukup tapi tidak minat → minat terlalu rendah untuk rekomendasi",
    "R5": "IP cukup + ada minat → keseimbangan moderat",
    "R6": "IP cukup + sangat suka → minat kuat mengkompensasi",
    "R7": "IP bagus tapi tidak suka → hanya Sedang (kunci: nilai tanpa minat)",
    "R8": "IP bagus + suka → kombinasi ideal, rekomendasi kuat",
    "R9": "IP bagus + sangat suka → rekomendasi terkuat",
}


# ═══════════════════════════════════════════════════════════════════════
# FIS Mamdani
# ═══════════════════════════════════════════════════════════════════════

def mamdani_cog(ip: float, minat: float, n: int = 10_001) -> dict:
    """
    Menjalankan FIS Mamdani untuk satu pasangan (IP, Minat).
    Mengembalikan dict berisi semua tahap dan hasil COG.
    """
    # Tahap 1: Fuzzifikasi
    mu_ip = {k: tri(ip, *v) for k, v in MF_IP.items()}
    mu_minat = {k: tri(minat, *v) for k, v in MF_MINAT.items()}

    # Tahap 2: Evaluasi Aturan
    rule_results = []
    for label, ipk, mink, nkk in RULES:
        alpha = min(mu_ip[ipk], mu_minat[mink])
        rule_results.append({
            "label": label,
            "ip_key": ipk,
            "minat_key": mink,
            "konsekuen": nkk,
            "mu_ip": mu_ip[ipk],
            "mu_minat": mu_minat[mink],
            "alpha": alpha,
            "aktif": alpha > 0,
        })

    # Tahap 3 & 4: Implikasi + Agregasi
    y = np.linspace(0, 100, n)
    agg = np.zeros_like(y)

    for rr in rule_results:
        if not rr["aktif"]:
            continue
        a, b, c = MF_NK[rr["konsekuen"]]
        mu_k = tri_array(y, a, b, c)
        impl = np.minimum(rr["alpha"], mu_k)
        agg = np.maximum(agg, impl)

    # Tahap 5: Defuzzifikasi COG
    numerator = float(np.trapezoid(y * agg, y))
    denominator = float(np.trapezoid(agg, y))
    cog = numerator / denominator if denominator > 1e-12 else 0.0

    return {
        "input": {"ip": ip, "minat": minat},
        "fuzzifikasi": {"ip": mu_ip, "minat": mu_minat},
        "aturan": rule_results,
        "cog": cog,
        "numerator": numerator,
        "denominator": denominator,
    }


def rekomendasi_kbks(ip_itp, minat_itp, ip_rpld, minat_rpld, ip_skjk, minat_skjk):
    """
    Menghitung NK untuk 3 KBK dan menentukan rekomendasi.
    """
    nk_itp = mamdani_cog(ip_itp, minat_itp)
    nk_rpld = mamdani_cog(ip_rpld, minat_rpld)
    nk_skjk = mamdani_cog(ip_skjk, minat_skjk)

    scores = {
        "ITP": nk_itp["cog"],
        "RPLD": nk_rpld["cog"],
        "SKJK": nk_skjk["cog"],
    }
    rekomendasi = max(scores, key=scores.get)

    return {
        "nk": scores,
        "rekomendasi": rekomendasi,
        "detail": {"ITP": nk_itp, "RPLD": nk_rpld, "SKJK": nk_skjk},
    }


# ═══════════════════════════════════════════════════════════════════════
# Data Survei 20 Mahasiswa
# Format: (no, ip_itp, minat_itp, ip_rpld, minat_rpld, ip_skjk, minat_skjk, pilihan)
# ═══════════════════════════════════════════════════════════════════════

DATA_MAHASISWA = [
    (1,  3.80, 3.60, 3.20, 2.00, 3.00, 1.50, "ITP"),
    (2,  3.60, 3.40, 3.00, 2.40, 2.80, 1.20, "ITP"),
    (3,  3.75, 3.80, 3.40, 2.20, 3.10, 1.40, "ITP"),
    (4,  3.50, 3.60, 3.00, 2.40, 2.60, 1.00, "ITP"),
    (5,  3.70, 3.40, 3.20, 2.20, 2.80, 1.80, "ITP"),
    (6,  3.60, 3.60, 3.30, 2.80, 3.00, 1.60, "ITP"),
    (7,  3.80, 3.20, 3.10, 2.00, 2.90, 1.60, "ITP"),
    (8,  2.60, 1.60, 3.60, 3.80, 3.00, 2.00, "RPLD"),
    (9,  2.80, 2.00, 3.80, 3.60, 3.20, 2.40, "RPLD"),
    (10, 2.20, 1.80, 3.50, 3.20, 2.60, 2.00, "RPLD"),
    (11, 2.00, 1.60, 3.70, 3.60, 3.00, 2.20, "RPLD"),
    (12, 3.00, 2.00, 3.60, 3.40, 3.30, 2.60, "RPLD"),
    (13, 2.40, 1.60, 3.60, 3.60, 3.00, 2.40, "RPLD"),
    (14, 2.60, 1.20, 2.80, 1.60, 3.80, 3.80, "SKJK"),
    (15, 2.20, 1.40, 2.60, 1.80, 3.90, 3.60, "SKJK"),
    (16, 2.40, 1.20, 2.80, 2.00, 3.70, 3.60, "SKJK"),
    (17, 3.00, 1.80, 2.40, 1.60, 3.80, 3.80, "SKJK"),
    (18, 2.80, 2.00, 2.60, 1.80, 3.90, 3.60, "SKJK"),
    (19, 2.40, 1.60, 2.80, 2.00, 3.80, 3.40, "SKJK"),
    (20, 3.40, 2.60, 3.52, 2.80, 3.65, 1.50, "?"),  # TARGET → harus RPLD
]


# ═══════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 78)
    print("SPK PEMILIHAN KBK — SISTEM INFERENSI FUZZY METODE MAMDANI")
    print("Ujian CPMK-2: Kecerdasan Buatan (MTE25112)")
    print("=" * 78)

    # ── 1. Tampilkan Membership Functions ─────────────────────────────
    print("\n" + "─" * 78)
    print("MEMBERSHIP FUNCTIONS")
    print("─" * 78)

    print("\nVariabel IP (semesta 0-4):")
    for k, (a, b, c) in MF_IP.items():
        print(f"  {k:>12}: segitiga ({a}, {b}, {c})")

    print("\nVariabel Minat (semesta 0-4):")
    for k, (a, b, c) in MF_MINAT.items():
        print(f"  {k:>12}: segitiga ({a}, {b}, {c})")

    print("\nVariabel NK / Output (semesta 0-100):")
    for k, (a, b, c) in MF_NK.items():
        print(f"  {k:>12}: segitiga ({a}, {b}, {c})")

    # ── 2. Tampilkan 9 Fuzzy Rules ───────────────────────────────────
    print("\n" + "─" * 78)
    print("9 FUZZY RULES")
    print("─" * 78)
    for label, ipk, mink, nkk in RULES:
        print(f"  {label}: IF IP={ipk:>11} AND Minat={mink:>12} → NK = {nkk:>7}")
        print(f"       ({RULE_JUSTIFICATIONS[label]})")

    # ── 3. Proses semua 20 data ──────────────────────────────────────
    print("\n" + "─" * 78)
    print("HASIL REKOMENDASI 20 MAHASISWA")
    print("─" * 78)

    benar = 0
    total = 0

    print(f"\n{'No':>3} {'Pilihan':>7} | {'NK_ITP':>8} {'NK_RPLD':>8} {'NK_SKJK':>8}"
          f" | {'Rekomendasi':>12} | {'Status':>8}")
    print("─" * 78)

    for row in DATA_MAHASISWA:
        no, ip_i, m_i, ip_r, m_r, ip_s, m_s, pilihan = row
        res = rekomendasi_kbks(ip_i, m_i, ip_r, m_r, ip_s, m_s)

        nk = res["nk"]
        rek = res["rekomendasi"]

        if pilihan != "?":
            status = "BENAR" if rek == pilihan else f"SALAH ({pilihan})"
            if rek == pilihan:
                benar += 1
            total += 1
        else:
            status = f"TARGET → {rek}"

        print(f"{no:>3} {pilihan:>7} | {nk['ITP']:>8.2f} {nk['RPLD']:>8.2f}"
              f" {nk['SKJK']:>8.2f} | {rek:>12} | {status:>8}")

    print("─" * 78)
    if total > 0:
        print(f"Akurasi data training: {benar}/{total} = {benar/total*100:.1f}%")

    # ── 4. Detail data target #20 ────────────────────────────────────
    print("\n" + "─" * 78)
    print("DETAIL DATA TARGET #20")
    print("─" * 78)

    row20 = DATA_MAHASISWA[-1]
    no, ip_i, m_i, ip_r, m_r, ip_s, m_s, _ = row20
    res20 = rekomendasi_kbks(ip_i, m_i, ip_r, m_r, ip_s, m_s)

    for kbk in ["ITP", "RPLD", "SKJK"]:
        detail = res20["detail"][kbk]
        ip_val = detail["input"]["ip"]
        minat_val = detail["input"]["minat"]
        print(f"\n--- KBK: {kbk} (IP={ip_val}, Minat={minat_val}) ---")

        # Fuzzifikasi
        fb = detail["fuzzifikasi"]["ip"]
        fm = detail["fuzzifikasi"]["minat"]
        print(f"  Fuzzifikasi IP:")
        for k, v in fb.items():
            print(f"    μ_{k}({ip_val}) = {v:.4f}")
        print(f"  Fuzzifikasi Minat:")
        for k, v in fm.items():
            print(f"    μ_{k}({minat_val}) = {v:.4f}")

        # Rules aktif
        print(f"  Rules aktif:")
        for r in detail["aturan"]:
            if r["aktif"]:
                print(f"    {r['label']}: {r['ip_key']}×{r['minat_key']}"
                      f" → {r['konsekuen']}, α = min({r['mu_ip']:.4f},"
                      f" {r['mu_minat']:.4f}) = {r['alpha']:.4f}")

        print(f"  NK (COG) = {detail['cog']:.4f}")

    print(f"\n{'='*78}")
    rek20 = res20["rekomendasi"]
    if rek20 == "RPLD":
        print("VERIFIKASI BERHASIL: Data #20 merekomendasikan RPLD ✓")
    else:
        print(f"VERIFIKASI GAGAL: Data #20 merekomendasikan {rek20} ✗")
    print(f"{'='*78}")

    # ── 5. Analisis Decision Boundary ────────────────────────────────
    print("\n" + "─" * 78)
    print("ANALISIS DECISION BOUNDARY")
    print("─" * 78)
    print("""
Decision boundary memetakan NK sebagai fungsi dari IPK dan Minat.
Chart ini menjawab: "Jika IPK dan Minat-nya sekian, NK-nya berapa?"

Cara membaca:
  Sumbu X = IPK (0-4)    Sumbu Y = Minat (0-4)
  Warna merah  = NK rendah (0-50)
  Warna kuning = NK sedang (50-75)
  Warna hijau  = NK tinggi (75-100)

Interpretasi data target #20:""")

    for kbk, idx, marker in [("ITP", 0, "○"), ("RPLD", 1, "□"), ("SKJK", 2, "△")]:
        ip_v = [ip_i, ip_r, ip_s][idx]
        m_v = [m_i, m_r, m_s][idx]
        nk_v = res20["nk"][kbk]
        zone = "hijau (NK tinggi)" if nk_v >= 75 else ("kuning (NK sedang)" if nk_v >= 50 else "merah (NK rendah)")
        print(f"  {marker} {kbk:4s}: ({ip_v}, {m_v}) → zona {zone}, NK = {nk_v:.2f}")

    print("""
Kesimpulan visual:
  • RPLD jatuh di zona HIJAU (kombinasi terbaik)
  • ITP jatuh di zona KUNING-HIJAU (cukup baik)
  • SKJK jatuh di zona MERAH-KUNING (minat terlalu rendah)
  • Area kanan bawah (IP tinggi, Minat rendah) tetap rendah
    → ini konsekuensi Rule R7: IP bagus tanpa minat hanya Sedang
  • NK tinggi HANYA tercapai jika IPK dan Minat keduanya memadai
""")
