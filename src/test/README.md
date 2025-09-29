# 🧪 Carpeta de Tests

En esta carpeta se encuentran todos los **tests de la gramática y semántica** de Compiscript.  
Cada subcarpeta contiene scripts para **crear** y **eliminar** sus archivos de prueba:

- `00-create_files.sh` -> crea los tests `.cps`.  
- `01-drop_files.sh` -> elimina los tests creados.  

> Nota: los archivos `.sh` se deben ejecutar desde la raiz del repositorio.

## ▶️ Ejecución de tests

### Crear o eliminar tests de una carpeta específica

Ejemplo con los de **TAC**:

```bash
./src/test/tac/00-create_files.sh
./src/test/tac/01-drop_files.sh
```

### Crear o eliminar **todos los tests**

```bash
./scripts/create_all.sh
./scripts/drop_all.sh
```

### Ejecutar un test específico

Por defecto se ejecuta `program.cps`, pero puedes correr uno en particular:

```bash
CPS_VERBOSE=0 ./scripts/run.sh src/carpeta/archivo.cps 
CPS_VERBOSE=1 ./scripts/run.sh src/carpeta/archivo.cps
```

- `CPS_VERBOSE=0` (por defecto) -> ejecución rápida, sin logs extensivos.
- `CPS_VERBOSE=1` -> genera logs detallados.

### Ejecutar en lote

Corre todos los archivos `.cps` dentro de `src/test/tac/` (esta ruta puede ser modificada dentro del archivo `run_files.sh`):

```bash
./scripts/run_files.sh
```

## 📂 Tipos de tests por carpeta

- **`arreglos/`**
  Validación de arreglos: índices válidos/erróneos, literales homogéneos/heterogéneos.

- **`clases_objetos/`**
  Definición de clases, constructores, métodos, herencia, acceso a atributos, `this`, errores comunes en propiedades.

- **`control_flujo/`**
  Uso de `if`, `while`, `for`, `switch`, incluyendo errores por condiciones no booleanas, `break` fuera de bucle, etc.

- **`declaraciones_asignaciones/`**
  Declaración de variables y constantes, inicialización, asignaciones correctas e incompatibles.

- **`expresiones/`**
  Operaciones aritméticas, lógicas y comparaciones. Casos válidos y errores por tipos incompatibles.

- **`funciones/`**
  Validación de firmas, número y tipo de parámetros, retornos correctos/incorrectos, recursión, closures.

- **`generales/`**
  Casos generales como **código muerto** (sentencias después de `return`).

- **`literales_identificadores/`**
  Uso correcto e incorrecto de literales, identificadores no declarados.

- **`smoke/`**
  Tests mínimos de humo: declaraciones simples, archivo vacío, etc.

- **`tac/`**
  Tests más completos de integración: expresiones, flujo de control, clases, arreglos, closures, manejo de OOB (out-of-bounds), generación de TAC en múltiples escenarios.
