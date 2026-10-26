#!/bin/bash
# One command to (re)build the QR codes: ./run.sh
# Sets up the Python environment on first run, then opens the output folder.
set -e
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -q -r requirements.txt

.venv/bin/python make_qr.py
open output
