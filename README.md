# Compis Script 🧠

Pequeño compilador/analizador para **Compis Script**: gramática ANTLR, análisis semántico y generación de **TAC (Three Address Code)** con reportes HTML (AST y tabla de símbolos).

## 🛠️ Entorno de desarrollo

- **ANTLR Parser Generator**: v4.13.1  
- **Python**: 3.10.12  
- **pip**: 25.2  
- **Docker**: 28.3.0 (build 38b7060)  
- **WSL2 (Windows Subsystem for Linux)**: v22.4.5 (o superior)  

## Resultado TAC programa oficial

```bash
CPS_VERBOSE=1 ./scripts/run.sh ./src/test/program.cps
========================================================================================================================

Ejecutando con archivo: ./src/test/program.cps
Tiempos:
        Léxica:     0.009s
        Sintáctica: 0.108s
        Semántica:  17.652s
        TAC:        18.735s
Tiempo total: 36.504s
OUT DIR: /mnt/d/repositorios/UVG/2025/pcompiler_construction_/src/logs/out/20251006-204640_program.cps
========================================================================================================================

=== TAC generado ===
; Compiscript TAC
; program: 20251006-204640_program.cps
; generated: 2025-10-06T20:46:58

FUNCTION toString:
        RETURN ""
END FUNCTION toString

FUNCTION Persona_constructor:
        this.nombre = fp[16]
        this.edad = fp[24]
        this.color = "rojo"
END FUNCTION Persona_constructor

FUNCTION Persona_saludar:
        t1 = this.nombre
        t2 := "Hola, mi nombre es " + t1
        RETURN t2
END FUNCTION Persona_saludar

FUNCTION Persona_incrementarEdad:
        t1 = this.edad
        t2 := t1 + fp[16]
        this.edad = t2
        t3 = this.edad
        PARAM t3
        CALL toString, 1
        t4 := R
        t2 := "Ahora tengo " + t4
        t5 := t2 + " años."
        RETURN t5
END FUNCTION Persona_incrementarEdad

FUNCTION Estudiante_constructor:
        this.nombre = fp[16]
        this.edad = fp[24]
        this.color = "rojo"
        this.grado = fp[28]
END FUNCTION Estudiante_constructor

FUNCTION Estudiante_estudiar:
        t1 = this.nombre
        t2 := t1 + " está estudiando en "
        t3 = this.grado
        PARAM t3
        CALL toString, 1
        t4 := R
        t5 := t2 + t4
        t6 := t5 + " grado."
        RETURN t6
END FUNCTION Estudiante_estudiar

FUNCTION Estudiante_promedioNotas:
        t1 := fp[16] + fp[20]
        t2 := t1 + fp[24]
        t3 := t2 / 3
        fp[4] := t3
        RETURN fp[4]
END FUNCTION Estudiante_promedioNotas

        gp[0] := ""
        gp[8] := "Erick"
        t4 = newobj Estudiante, 24
        PARAM t4
        PARAM gp[8]
        PARAM 20
        PARAM 3
        CALL Estudiante_constructor, 4
        gp[16] := t4
        PARAM gp[16]
        CALL Persona_saludar, 1
        t4 := R
        t1 := gp[0] + t4
        t3 := t1 + "\n"
        gp[0] := t3
        PARAM gp[16]
        CALL Estudiante_estudiar, 1
        t5 := R
        t3 := gp[0] + t5
        t2 := t3 + "\n"
        gp[0] := t2
        PARAM gp[16]
        PARAM 5
        CALL Persona_incrementarEdad, 2
        t6 := R
        t2 := gp[0] + t6
        t7 := t2 + "\n"
        gp[0] := t7
        gp[24] := 1
WHILE_START1:
        t8 := gp[24] <= 5
        IF t8 > 0 GOTO WHILE_BODY2
        GOTO WHILE_END3
WHILE_BODY2:
        t3 := gp[24] % 2
        t9 := t3 == 0
        IF t9 > 0 GOTO IF_THEN4
        GOTO IF_ELSE6
IF_THEN4:
        PARAM gp[24]
        CALL toString, 1
        t5 := R
        t3 := gp[0] + t5
        t1 := t3 + " es par\n"
        gp[0] := t1
        GOTO IF_END5
IF_ELSE6:
        PARAM gp[24]
        CALL toString, 1
        t4 := R
        t1 := gp[0] + t4
        t2 := t1 + " es impar\n"
        gp[0] := t2
IF_END5:
        t2 := gp[24] + 1
        gp[24] := t2
        GOTO WHILE_START1
WHILE_END3:
        t10 = gp[16].edad
        t2 := t10 * 2
        t7 := 5 - 3
        t11 := t7 / 2
        t7 := t2 + t11
        gp[28] := t7
        t1 := gp[0] + "Resultado de la expresión: "
        PARAM gp[28]
        CALL toString, 1
        t5 := R
        t7 := t1 + t5
        t3 := t7 + "\n"
        gp[0] := t3
        gp[32] := 0
        PARAM gp[16]
        PARAM 90
        PARAM 85
        PARAM 95
        CALL Estudiante_promedioNotas, 4
        t10 := R
        gp[32] := t10
        t7 := gp[0] + "Promedio (entero): "
        PARAM gp[32]
        CALL toString, 1
        t5 := R
        t1 := t7 + t5
        t3 := t1 + "\n"
        gp[0] := t3

====================
```

## ⚡️ Quickstart

```bash
# 1) Instalar deps
./scripts/setup.sh

# 2) Generar lexer/parser de ANTLR -> antlr_gen/
./scripts/generate_code_py.sh

# 3) Ejecutar un test (por defecto program.cps si no pasas archivo)
CPS_VERBOSE=0 ./scripts/run.sh src/test/program.cps
```

> `CPS_VERBOSE` por defecto es **0**. Usa **1** para logs detallados (tarda más).

## ▶️ Ejecución de pruebas

- **Un test específico**

  ```bash
  CPS_VERBOSE=0 ./scripts/run.sh src/test/program.cps
  CPS_VERBOSE=1 ./scripts/run.sh src/test/program.cps
  ```

- **Crear/borrar lote específico** (ej. `tac`)

  ```bash
  ./src/test/tac/00-create_files.sh
  ./src/test/tac/01-drop_files.sh
  ```

- **Correr lote** (por defecto usa `src/test/tac/`, editable en `./scripts/run_files.sh`)

  ```bash
  ./scripts/run_files.sh
  ```

- **Crear/Borrar TODOS los tests**

  ```bash
  ./scripts/create_all.sh
  ./scripts/drop_all.sh
  ```

> Más detalles en `src/test/README.md` (tipos de pruebas por carpeta) y significado de los scripts en `scripts/`.

## 🧾 Logs y reportes

Cada ejecución crea:

- Carpeta: `src/logs/out/<timestamp>_<archivo>.cps/`
- Archivos:

  - `ast.txt` y `ast.html` -> Árbol sintáctico.
  - `program.tac` y `program.tac.html` -> TAC.
  - `symbols.log` y `symbols.html` -> Tabla de símbolos.
  - `workflow.log` -> trazas de depuración.

## 📁 Estructura

```bash
antlr_gen/          # Código generado por ANTLR (Python)
docs/               # Diseño y notas (semántica, TAC, etc.)
ide/cps/            # Extensión VS Code (syntax highlight, parser JS)
scripts/            # setup, generate, run, batch (create_all/drop_all)
src/
  driver.py         # Punto de entrada
  ir/               # TAC, labels, temporales, RA, emitter
  logs/             # Logger + reporters (HTML)
  semantic/         # Análisis semántico (visitor, scopes, tipos)
  test/             # Suites de pruebas (+ scripts por carpeta)
  utils/            # Gramática ANTLR (Compiscript.g4)
```

## 🎨 Extensión para Compis Script en VS Code

Para habilitar **resaltado de sintaxis** de Compis Script en VS Code:

1. Instalar la extensión en windows:

    ```bash
    cd ide/
    ```

    ```bash
    $dest="$env:USERPROFILE\.vscode\extensions\cps"; try { New-Item -ItemType Directory -Force $dest | Out-Null; Copy-Item -Recurse -Force .\cps\* $dest -ErrorAction Stop; Write-Host "✅ Extensión instalada/actualizada en $dest" -ForegroundColor Green } catch { Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red; exit 1 }
    ```

3. Cierra y vuelve a abrir VS Code.
