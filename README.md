# SPK Pemilihan KBK — Fuzzy Inference System (Mamdani)

Ujian CPMK-2: Kecerdasan Buatan (MTE25112)

**RIYADI — H2A025002** | Magister Teknik Elektro, Universitas Jenderal Soedirman

## Deskripsi

Sistem Pendukung Keputusan (SPK) berbasis logika fuzzy untuk memilih Bidang Konsentrasi (KBK) di antara ITP, RPLD, dan SKJK berdasarkan IPK dan skor Minat.

## File

| File | Keterangan |
|------|------------|
| `app_streamlit.py` | Aplikasi web interaktif (Streamlit) |
| `sim_fuzzy_spk.py` | Simulasi FIS Mamdani (CLI) |
| `viz_presentasi.py` | Generator visualisasi (PDF) |
| `make_pptx.py` | Generator presentasi (PPTX) |
| `run.sh` | Setup venv + jalankan Streamlit |
| `ujian_cpmk_2.tex` / `.pdf` | Laporan IEEE format |
| `presentasi_cpmk2.pptx` | Slide presentasi |
| `plot_*.pdf` / `.png` | Visualisasi |

## Cara Menjalankan

### Streamlit (Web App)
```bash
chmod +x run.sh
./run.sh
```
Buka browser di `http://localhost:8501`

### CLI (Terminal)
```bash
python3 sim_fuzzy_spk.py
```

### Install Dependencies Manual
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install streamlit numpy matplotlib python-pptx
```

## Metode

- **Fuzzifikasi**: 3 MF segitiga per variabel (IP: Kecil/Cukup/Bagus, Minat: Tidak Suka/Suka/Sangat Suka)
- **Rules**: 9 aturan fuzzy (3x3 matriks)
- **Inferensi**: Mamdani (implikasi=min, agregasi=max)
- **Defuzzifikasi**: Centre of Gravity (COG)

## Hasil

- Akurasi 19 data latih: **100%**
- Data target #20: **RPLD** (NK=75.00 > NK_ITP=71.14 > NK_SKJK=50.00)
