#!/bin/bash

echo "Creando entorno virtual..."
python3 -m venv venv

echo "Instalando dependencias..."
source venv/bin/activate
pip install -r ./requirements.txt
deactivate

echo "Entorno listo. Puedes ejecutar ./scripts/generate_code_py.sh para generar el código python."

