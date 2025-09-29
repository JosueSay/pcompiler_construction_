# Compis Script 🧠

Pequeño compilador/analizador para **Compis Script**: gramática ANTLR, análisis semántico y generación de **TAC (Three Address Code)** con reportes HTML (AST y tabla de símbolos).

## 🛠️ Entorno de desarrollo

- **ANTLR Parser Generator**: v4.13.1  
- **Python**: 3.10.12  
- **pip**: 25.2  
- **Docker**: 28.3.0 (build 38b7060)  
- **WSL2 (Windows Subsystem for Linux)**: v22.4.5 (o superior)  

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

1. Copia la extensión al directorio de VS Code:

   ```bash
   cd ide/
   cp -r cps ~\.vscode\extensions\
   ```

2. Cierra y vuelve a abrir VS Code.
