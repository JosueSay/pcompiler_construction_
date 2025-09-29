#!/bin/bash

# Ruta de los .cps
RUTA="./src/test/tac"

# Mostrar contenidos de los archivos
for f in "$RUTA"/*.cps; do
  echo "===== $f ====="
  cat "$f"
  echo
done

# Recorre todos los archivos .cps y los pasa a run.sh
for f in "$RUTA"/*.cps; do
  echo ">> Ejecutando $f"
  CPS_VERBOSE=1 ./scripts/run.sh "$f"
  echo ""
done
