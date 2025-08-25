# Tests de Compiscript

## Cómo correr

* **Un test**:

  ```bash
  CPS_VERBOSE=0 ./scripts/run.sh src/test/<carpeta>/<archivo>.cps
  ```

* **Todos los tests**:

  ```bash
  find src/test -name "*.cps" -print0 | xargs -0 -n1 -I{} bash -c 'CPS_VERBOSE=0 ./scripts/run.sh "{}"'
  ```

* Los artefactos (AST/tabla de símbolos/log) quedan en `src/logs/out/`. El script muestra una URL local para verlos.

## Convenciones

* **Éxito:** archivos `success_*.cps` → no deben emitir `SemanticError` ni `DeadCode`.
* **Error:** archivos `error_*.cps` → deben emitir al menos un diagnóstico esperado (ejemplos:
  `Número de argumentos inválido`, `Uso de variable no declarada`, `Tipo de 'case' incompatible`, `Código inalcanzable`, etc.).
* **Un caso por archivo** (máx. 10–20 líneas) para aislar fallos.
* **Sin `float`**: la gramática no lo soporta; no crear casos con `float`.

## Estructura

```bash
test/
  smoke/                      # sanity checks mínimos
  literales_identificadores/  # literales y uso de identificadores
  declaraciones_asignaciones/ # let/const, asignaciones, tipos
  expresiones/                # aritmética, lógica, comparaciones
  arreglos/                   # literales homogéneos, indexación
  control_flujo/              # if/while/for/foreach/switch/break/continue
  funciones/                  # params, retorno, recursión, closures
  clases_objetos/             # atributos, métodos, constructor, herencia
  generales/                  # reglas transversales (código muerto)
  program.cps                 # programa demo integrado
  debug.cps                   # espacio para pruebas ad-hoc
```
