#!/usr/bin/env bash
# run_all.sh - Linux / macOS / WSL / Git Bash
set -e

if [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
else
  echo "No se encontro venv/bin/activate. Asegurate de haber creado el entorno virtual."
  exit 1
fi

echo "Ejecutando run_all.py con el python del venv..."
python run_all.py
RC=$?
echo "run_all finalizo con codigo ${RC}"
exit ${RC}
