# Implementación Fase TAC (3AC)

Este documento describe **lo que efectivamente se implementó** en la fase de generación de **Three-Address Code (TAC/3AC)** del compilador de Compiscript: decisiones finales, funcionalidades clave, particularidades del emisor, y guías para entender y extender el código.

## 1. Resumen ejecutivo (estrategia aplicada)

* **Única pasada semántica + emisión TAC**: las visitas semánticas emiten cuádruplos en el momento, evitando una segunda pasada.
* **Representación dual**:

  * **Texto 3AC** con etiquetas (`Lk:`), pensado para inspección y pruebas golden.
  * **Cuádruplos en memoria** con campos `op, arg1, arg2, res, label` (cuando aplica).
* **Pools de temporales por sentencia**: reciclaje determinista y reset al final de cada statement para evitar fugas.
* **Control de flujo con etiquetas**: patrones canónicos para `if/else`, `while`, `do-while`, `for`, `switch`.
* **Chequeos de seguridad en arreglos**: *bounds check* siempre **antes** de `INDEX_LOAD/STORE`.
* **Modelo de RA explícito**: pseudo-instrucción `enter f, frame_size` y convención `param …` + `call f, n`.
* **Clases y campos**: `FIELD_LOAD`/`FIELD_STORE` con metadatos `_field_owner/_field_offset` cuando aplica.
* **Closures**: `mkenv` + `mkclos` + `callc` soportados para capturas por entorno.

## 2. Alcance implementado (funcionalidades principales)

### Expresiones y asignaciones

* Aritméticas binarias/unarias, relacionales, lógicas con corto-circuito (no se materializan bools intermedias si no es necesario).
* Asignaciones a:

  * **Variable simple**: `x = expr`.
  * **Indexada**: `a[i] = expr` y `x = a[i]` con **bounds check**.
  * **Propiedad**: `obj.f = expr` y `x = obj.f`.
  * **Cadenas de propiedades** seguidas de indexación: `a.b.c[i] = v` (resueltas con `FIELD_LOAD` en cadena + check + `INDEX_STORE`).

### Control de flujo

* `if`, `if/else` con corto-circuito canónico.
* `while`, `do-while`, `for` (desazucarado a `while` con etiquetas `Lstart/Lbody/Lstep/Lend`).
* `switch` con saltos a `case/default` y manejo explícito de *fallthrough*.
* `break`/`continue` soportados por saltos dirigidos.

### Funciones, métodos y RA

* `enter f_label, local_frame_size`.
* `param x`, `call f_label, n` / `t = call f_label, n`, `return`/`return v`.
* **Métodos de clase** con `this` implícito (primer “parámetro” lógico).
* **Closures**: `t_env = mkenv <capturas>`; `t_clos = mkclos f_label, t_env`; `callc t_clos, n`.

### Clases y campos

* `FIELD_LOAD obj.f -> t` y `FIELD_STORE obj.f = v`.
* Atributos con `offset` calculado por `ClassHandler`; los *quads* pueden anotar `_field_owner/_field_offset`.

### Arreglos y seguridad

* **Siempre**: `t_len = len a; if i<0 goto oob; if i>=t_len goto oob; …; a[i]=v|t=a[i]`.
* En `oob`: `call __bounds_error, 0`.

### Diagnósticos y barreras

* **Const-safety**: error al asignar a constantes o a propiedades a través de constantes.
* **Tipado indexado**: índice debe ser entero; RHS compatible con `elem_type`.
* **Código muerto**: tras `return` en un bloque, se marca *dead code* y no se emite TAC útil.
* Mensajes claros y predicibles (los viste en los tests).

## 3. Emisor TAC y gestión de temporales

* **Temporales por tipo** (`int`, `bool`, `ref`, …) y **reset por sentencia**.
* Regla de liberación: **post-orden** en el padre; si el valor se propaga como `place` de la expresión, no se libera.
* **Labels** generados con contador monótono: `Lstart1/Lbody2/Lend3`, etc., por estructura.
* `enter` se emite al inicio de cada función/método con el `frame_size` que entrega `ScopeManager` al cerrar el scope.

## 4.Patrones de traducción: fragmentos reales

### a. Bounds check antes de store

```text
t3 = len a
if i<0 goto oob1
if i>=t3 goto oob1
goto ok2
oob1:
call __bounds_error, 0
ok2:
a[i] = v
```

### b. Acceso encadenado y luego índice

```text
t2 = a.b
t3 = t2.c
t4 = len t3
if 1<0 goto oob1
if 1>=t4 goto oob1
goto ok2
oob1:
call __bounds_error, 0
ok2:
t3[1] = 3
```

### c. Corto-circuito típico

```text
if x<3||y>7&&x!=y goto Lthen1
goto Lelse3
...
```

### d. Método con `this` y `enter`

```text
f_Box_get:
enter f_Box_get, 12
t1 = this.data
t3 = len t1
if i<0 goto oob1
if i>=t3 goto oob1
goto ok2
oob1:
call __bounds_error, 0
ok2:
t2 = t1[i]
return t2
```

### e. Closure con entorno

```text
f_add:
enter f_add, 4
t1 = base + n
return t1
t2 = mkenv base
t3 = mkclos f_add, t2
param 5
t1 = callc t3, 1
```

## 5. Invariantes y “gotchas”

* **Siempre** emitir *bounds check* antes de cualquier `INDEX_LOAD/STORE` (incluye casos con índice temporal).
* **Nunca** materializar bools intermedios para `&&`/`||` en contexto de control; usar saltos (DDS).
* **Liberar** `t_len` y otros temporales de checks/índices tras el store/load y **antes** del `resetPerStatement`.
* En **`obj.prop[i] = v`**:

  1. `FIELD_LOAD` hasta el arreglo,
  2. *bounds check* sobre el **place** del arreglo,
  3. `INDEX_STORE` y **liberar** el temporal del arreglo.
* **`this`** sólo es válido en métodos; uso fuera de clase → error (se reporta y no se emite store).
* **Constantes**: se permite usarlas como RHS; no como LHS ni como base de store indexado.

## 6. Cómo leer el *output* de pruebas

* Cada archivo `.cps` genera un directorio bajo `src/logs/out/<timestamp>_archivo.cps` con:

  * TAC textual final,
  * (opcional) versión HTML,
  * logs semánticos.
* Las pruebas cubren:

  * **Éxitos** (p. ej., `class_test_v01.cps`, `indice_lectura_y_escritura.cps`, `integracion_mixta_d2.cps`),
  * **Errores** (tipo de índice, incompatibilidades de asignación, *dead code*, `this` inválido, `const` no modificable),
  * **Cadenas largas** con propiedades + índice,
  * **Closures** y **recursión** (factorial).

## 7. Extensiones previstas (sin bloquear lo actual)

* **Optimizaciones locales** (copy-prop, const-folding, DCE posterior a *dead code* de alto nivel).
* **Análisis de *liveness* global** para mejor reutilización de temporales entre sentencias.
* **Desugar explícito de `foreach`** (si la gramática lo incluye) a un patrón `for` con iterador.
* **Modelo de *static link*** en RA para *nested functions* (si se proyecta código nativo).
* **Chequeos nulos** (`null-checks`) para accesos a referencias si se habilita semántica *nullable*.

## 8. Pistas para contribuir / ubicar código

* **Emisión TAC**: `Emitter` (cuádruplos + buffer textual) con `emit`, `newlabel`, `temp_pool`.
* **Visitantes**: `VisitorCPS` orquesta; *statements/expressions analyzers* emiten TAC y devuelven `ExprRes {type, place, is_temp}`.
* **Clases**: `ClassHandler` resuelve tipos de campos y offsets (`get_attribute_type`, `get_field_offset`).
* **Símbolos y scopes**: `ScopeManager` calcula `frameSize()` al cerrar y lo persiste en el símbolo de la función/método.
* **Checks de límites**: helper `emitBoundsCheck(idx_place, arr_place)` devuelve (temporal_len, label_ok).

## 9. Mini “FAQ”

* **¿Por qué hay `enter f, N`?**
  Para fijar en el TAC el tamaño del marco local con el que se validan llamadas y activaciones. Es una **pseudo-op** informativa.

* **¿Por qué dos `len` y dos checks en `read` seguido de `write`?**
  Cada acceso (lectura o escritura) protege su propia ventana; el *hoisting* de checks se deja para una fase de optimización posterior.

* **¿Qué pasa si el índice es constante (p. ej., `0`)**?
  Igual se genera `len` + check; la **correctitud prima** sobre el *strength reduction* en esta fase.

## 10. Ejemplos rápidos (de los tests)

* **Escritura indexada segura** (`class_test_v02.cps`):

  ```text
  t2 = len x
  if 0<0 goto oob1
  if 0>=t2 goto oob1
  ...
  x[0] = 9
  ```

* **Propiedad + índice en método** (`class_test_v12.cps`):

  ```text
  t1 = this.data
  t2 = len t1
  ...
  t1[i] = v
  ```

* **Cadenas de propiedades** (`class_test_v09.cps`):

  ```text
  t2 = a.b
  t3 = t2.c
  ...
  t3[1] = 3
  ```
