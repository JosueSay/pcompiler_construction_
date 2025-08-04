#!/bin/bash

echo -e "Inicio en generación de código python...\n"

# Cargar variables del entorno si existe .env
if [ -f .env ]; then
  echo -e "\t- Cargando configuración desde .env"
  source .env
else
  echo -e "\t- No se encontró .env, usando ruta por defecto para ANTLR"
fi

# Usar valor por defecto si ANTLR_PATH en .env no está definido
ANTLR_PATH="${ANTLR_PATH:-scripts/antlr-4.13.1-complete.jar}"
ANTLR_PATH=$(realpath "$ANTLR_PATH")

echo -e "\n\t- Ruta actual:"
echo -e "\t\t $(pwd)"

FLAG=false
GRAMMAR_PATH="src/utils"
GRAMMAR_FILE="Compiscript.g4"
OUTPUT_DIR="antlr_gen"

echo -e "\n\t- Cambiando a la ruta:"
cd "$GRAMMAR_PATH" || exit 1
echo -e "\t\t $(pwd)"

# echo -e "\n\t- Ruta de salida:"
# echo -e "\t\t../../$OUTPUT_DIR"

# Ejecutar ANTLR usando Java + JAR
if java -jar "$ANTLR_PATH" -Dlanguage=Python3 -o "../../$OUTPUT_DIR" "$GRAMMAR_FILE"; then
  FLAG=true
fi

# Volver al directorio anterior
cd - > /dev/null

# Verificar si funcionó
if [ "$FLAG" = true ]; then
  echo -e "\nGeneración completa. Los archivos estan en $OUTPUT_DIR/"
else
  echo -e "\nFalló la generación de código."
fi
