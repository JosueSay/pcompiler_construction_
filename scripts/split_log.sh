#!/bin/bash
# CPS_VERBOSE=0 ./scripts/run_files.sh --no-color > results.log
# sed -r "s/\x1B\[[0-9;]*[mK]//g" results.log > results_clean.log

exec_log="results_clean.log"
RUTA="./src/test/tac"
output_dir="./results"
mkdir -p "$output_dir"

declare -A codigos
declare -A ejecuciones
declare -A outdirs

# 1. Guardar contenido de cada .cps
for f in "$RUTA"/*.cps; do
    nombre=$(basename "$f" .cps)
    codigos["$nombre"]="$(cat "$f")"
done

# 2. Capturar ejecución y OUT DIR de results.log
current_file=""
buffer=""
capturando=0

while IFS= read -r line; do
    if [[ $line =~ ^Ejecutando\ con\ archivo:\ (.+\.cps) ]]; then
        current_file=$(basename "${BASH_REMATCH[1]}" .cps)
        buffer="$line"$'\n'
        capturando=1
    elif [[ $capturando -eq 1 ]]; then
        buffer+="$line"$'\n'
        # Guardar OUT DIR
        if [[ $line =~ ^OUT\ DIR:\ (.+)$ ]]; then
            outdirs["$current_file"]="${BASH_REMATCH[1]}"
        fi
        # Fin del bloque de ejecución
        if [[ $line == "" ]]; then
            ejecuciones["$current_file"]="$buffer"
            buffer=""
            capturando=0
        fi
    fi
done < "$exec_log"

# 3. Crear logs finales con código + ejecución + TAC desde OUT DIR/program.tac
for nombre in "${!codigos[@]}"; do
    output="$output_dir/$nombre.log"
    echo "===== $nombre.cps =====" > "$output"
    echo "${codigos[$nombre]}" >> "$output"
    echo "" >> "$output"
    
    if [[ -n "${ejecuciones[$nombre]}" ]]; then
        echo "${ejecuciones[$nombre]}" >> "$output"
    else
        echo "Advertencia: No se encontró ejecución para $nombre.cps" >> "$output"
    fi

    # Agregar TAC desde OUT DIR/program.tac
    tac_file="${outdirs[$nombre]}/program.tac"
    if [[ -f "$tac_file" ]]; then
        echo "" >> "$output"
        echo "=== TAC generado (desde $tac_file) ===" >> "$output"
        cat "$tac_file" >> "$output"
        echo "====================" >> "$output"
    else
        echo "Advertencia: No se encontró $tac_file" >> "$output"
    fi
done

echo "Logs finales generados en $output_dir"
