#!/usr/bin/env bash
# Setup venv dan jalankan Streamlit app untuk SPK Fuzzy KBK
# Ujian CPMK-2: Kecerdasan Buatan (MTE25112)

set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$DIR/.venv"

echo "=== SPK Fuzzy — Pemilihan KBK ==="

# Buat venv jika belum ada
if [ ! -d "$VENV" ]; then
    echo "[1/3] Membuat virtual environment..."
    python3 -m venv "$VENV"
else
    echo "[1/3] Virtual environment sudah ada, skip."
fi

# Install dependencies
echo "[2/3] Install dependencies..."
"$VENV/bin/pip" install -q streamlit numpy matplotlib

# Jalankan app
echo "[3/3] Menjalankan Streamlit app..."
echo "      Buka browser di http://localhost:8501"
echo "      Tekan Ctrl+C untuk berhenti."
echo ""
"$VENV/bin/streamlit" run "$DIR/app_streamlit.py" --server.port 8501
