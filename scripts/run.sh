#!/bin/bash

# Activar entorno virtual
if [ ! -d "venv" ]; then
  echo "No se encontró el entorno virtual en ./venv"
  echo "Ejecuta ./scripts/setup.sh para crearlo primero."
  exit 1
fi

source venv/bin/activate
# echo "Entorno virtual activado."

# Archivo de entrada por defecto
DEFAULT_FILE="src/test/program.cps"
INPUT_FILE="${1:-$DEFAULT_FILE}"

# Verificar existencia del archivo
if [ ! -f "$INPUT_FILE" ]; then
  echo -e "\tEl archivo \"$INPUT_FILE\" no existe."
  exit 1
fi

# Ejecutar el driver con PYTHONPATH ajustado
echo -e "\nEjecutando con archivo: $INPUT_FILE"
echo -e "Visitar http://172.20.112.1:5500/src/logs/out/ para abrir los archivos correspondientes\n" 
PYTHONPATH=. python3 src/driver.py "$INPUT_FILE"
