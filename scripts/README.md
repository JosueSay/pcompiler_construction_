# ⚙️ Scripts del Proyecto

Esta carpeta contiene los scripts principales para configurar el entorno, generar código, crear/eliminar archivos de prueba y ejecutar programas.  
Todos los scripts deben ejecutarse desde la **raíz del proyecto**.

## 🚀 Configuración y entorno

Para preparar el entorno de desarrollo:

```bash
./scripts/setup.sh
```

Este script:

* Crea un entorno virtual de Python en `./venv`.
* Instala las dependencias desde `requirements.txt`.

## 🔧 Generar código con ANTLR

Una vez configurado el entorno, puedes generar el lexer y parser en Python a partir de la gramática `Compiscript.g4`:

```bash
./scripts/generate_code_py.sh
```

* Usa el JAR de ANTLR definido en `.env` o el valor por defecto.
* Genera los archivos dentro de `antlr_gen/`.

## 📂 Manejo de archivos de prueba

### Crear archivos de prueba

Ejecuta todos los scripts `00-create_files.sh` encontrados en `src/test/`:

```bash
./scripts/create_all.sh
```

### Eliminar archivos de prueba

Ejecuta todos los scripts `01-drop_files.sh` encontrados en `src/test/`:

```bash
./scripts/drop_all.sh
```

## ▶️ Ejecución de programas

### Ejecutar un archivo específico

Por defecto, se usa `src/test/program.cps`, pero puedes pasar otro archivo como argumento:

```bash
./scripts/run.sh [ruta_al_archivo.cps]
```

Ejemplo:

```bash
./scripts/run.sh src/test/ejemplo.cps
```

### Ejecutar todos los archivos `.cps` en lote

Ejecuta y muestra el contenido de todos los programas ubicados en `src/test/tac/` (esta ruta puede editarse modificando la ruta dentro del archivo `run_files.sh`):

```bash
./scripts/run_files.sh
```

>**Nota:** al correr los archivos `.cps` por lote por defecto se ejecutan sin registrar logs semánticos y TAC dado por la instrucción `CPS_VERBOSE=0`, en caso de querer registrar los logs del flujo de trabajo cambiar el valor de `0` a `1`.
