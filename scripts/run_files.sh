#!/bin/bash

# Ruta de los .cps
RUTA="./src/test/smoke"

# Mostrar contenidos de los archivos
for f in "$RUTA"/*.cps; do
  echo "===== $f ====="
  cat "$f"
  echo
done

# Recorre todos los archivos .cps y los pasa a run.sh
for f in "$RUTA"/*.cps; do
  CPS_VERBOSE=0 ./scripts/run.sh "$f"
  echo ""
done
