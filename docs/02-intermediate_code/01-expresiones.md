# Generación de TAC para Expresiones

Este documento describe **cómo está implementada** la generación de **Three-Address Code (TAC/3AC)** para **expresiones** en Compiscript: reglas efectivas de traducción, manejo de temporales y etiquetas, y particularidades confirmadas por la batería de pruebas (incluyendo acceso indexado, propiedades encadenadas, corto-circuito y `this`/métodos/closures).

## 1. Alcance y convenciones efectivas

* **Doble representación**:

  * **3AC textual** (archivo `.tac`) con etiquetas (`Lk:`), útil para “golden tests”.
  * **Cuádruplos** en memoria: `(op, arg1, arg2, res, label?)`.
* Cada visita de expresión retorna `ExprRes = { type, place, is_temp }`.
* **Emisión in situ** durante la visita semántica; no hay segunda pasada.
* **Temporales**:

  * Pools por tipo; **liberación post-orden** al emitir el padre, salvo que el valor suba como `place`.
  * **Reset al final de cada sentencia** (observado en los tests: no hay fugas entre statements).
* **Etiquetas**:

  * Se usan para control y corto-circuito.
  * Esquemas canónicos: `Lstart/Lbody/Lstep/Lend` en bucles, `Lthen/Lelse/Lend` en condicionales.
* **Convenciones extra confirmadas**:

  * `enter f_label, frame_size` al inicio de funciones/métodos.
  * `param …` + `call f, n` / `t = call f, n`; `return`/`return v`.

## 2. Aritméticas `+ - * /` y unaria `-`

### Regla práctica

```bash
L = visit(E1); R = visit(E2)
T = newtemp(type(E1 op E2))
emit(T = L.place op R.place)
freeIfTemp(L); freeIfTemp(R)
return {type, T, is_temp=True}
```

### Ejemplo real

```text
t1 = a + b
t2 = c - d
t3 = t1 * t2
z  = t3
```

**Notas**:

* Tipado por `type_system`.
* El backend podrá fusionar/copiar; la fase actual prioriza claridad 3AC.

## 3. Relacionales y booleanos con corto-circuito `&& || !`

### Contexto de **control** (preferido)

No se materializa `bool` intermedio: se emiten **saltos**.

```bash
if E1 rel E2 goto Ltrue
goto Lfalse
```

`||` y `&&` siguen reglas DDS con etiqueta intermedia:

* `B = B1 || B2`

  ```bash
  B1.true = Ltrue; B1.false = Lmid
  B2.true = Ltrue; B2.false = Lfalse
  code: B1; Lmid: B2
  ```

* `B = B1 && B2`

  ```bash
  B1.true = Lmid; B1.false = Lfalse
  B2.true = Ltrue; B2.false = Lfalse
  code: B1; Lmid: B2
  ```

### Contexto de **valor** (cuando debe producir 0/1)

Se materializa un temporal booleano con asignaciones condicionadas (patrón “relleno”).

### Ejemplo real (if con corto-circuito)

```text
if x<3||y>7&&x!=y goto Lthen1
goto Lelse3
...
```

## 4. Asignación simple `x = expr`

```bash
R = visit(expr)
emit(x = R.place)
freeIfTemp(R)
```

Ejemplo:

```text
t1 = y + 2
o.x = t1    ; si LHS es propiedad, ver §7
```

## 5. Lectura/Escritura indexada `x = a[i]` / `a[i] = x`

**Invariante:** siempre hay *bounds check* **antes** de cualquier `INDEX_LOAD/STORE` (incluyendo índices en temporales y literales).

### Patrón real (lectura)

```text
t3 = len a
if i<0  goto oob1
if i>=t3 goto oob1
goto ok2
oob1:  call __bounds_error, 0
ok2:   t2 = a[i]
x = t2
```

### Patrón real (escritura)

```text
t3 = len a
if i<0  goto oob1
if i>=t3 goto oob1
goto ok2
oob1:  call __bounds_error, 0
ok2:   a[i] = v
```

**Notas**:

* El temporal de `len` se **libera** tras el acceso.
* En secuencias lectura→escritura se repite el check (hoisting diferido a futuras optimizaciones).

## 6. Acceso a propiedad `obj.f` y cadenas `a.b.c`

* **Lectura**: `FIELD_LOAD` a un temporal (`t = obj.f`).
* **Escritura**: `FIELD_STORE` (`obj.f = v`).
* **Cadenas**: `FIELD_LOAD` en cascada hasta obtener el lugar del arreglo/valor final.

### Propiedad + índice (dos caminos cubiertos)

1. **this.prop[i] = v** (método):

```text
t1 = this.data
t2 = len t1
...
t1[i] = v
```

2. **a.b.c[i] = v** (encadenado):

```text
t2 = a.b
t3 = t2.c
t4 = len t3
...
t3[1] = 3
```

**Metadatos**: cuando aplica, los `FIELD_*` llevan `_field_owner/_field_offset` desde `ClassHandler`.
**Const-safety**: no se permite modificar constantes ni realizar “store” a través de una base `const`.

## 7. `this` en métodos

`this` está disponible como identificador **sólo** dentro de métodos; fuera de clase → error semántico y no se emite store.
Patrón típico (visto en getters/setters e incrementos):

```text
t1 = this.x
t2 = t1 + 1
this.x = t2
```

## 8. Constantes (`const`)

Se exige inicializador en semántica. En TAC:

```text
t1 = expr
K  = t1
```

Luego, cualquier intento de asignar a `K` o de usar `K[...] =` es error (detectado en semántica).

## 9. Closures (cuando hay funciones anidadas con captura)

Patrón efectivo:

```text
f_add:
enter f_add, N
t1 = base + n
return t1

t_env = mkenv base
t_clo = mkclos f_add, t_env
param 5
t1 = callc t_clo, 1
```

* `mkenv` empaqueta capturas, `mkclos` crea el cierre, `callc` invoca con entorno.

## 10. Pseudocódigo de los esquemas usados

### Binaria aritmética

```text
visitBinary(E1, op, E2):
  L = visit(E1)
  R = visit(E2)
  T = newtemp(type(E1 op E2))
  emit(T = L.place op R.place)
  freeIfTemp(L); freeIfTemp(R)
  return {type: T.type, place: T, is_temp: true}
```

### Relacional en control

```text
emitRelCond(E1, rel, E2, Ltrue, Lfalse):
  L = visit(E1); R = visit(E2)
  emit(if L.place rel R.place goto Ltrue)
  emit(goto Lfalse)
  freeIfTemp(L); freeIfTemp(R)
```

### Indexada segura (plantilla)

```text
emitBoundsCheck(i, a):
  t_len = len a
  if i<0  goto L_oob
  if i>=t_len goto L_oob
  goto L_ok
L_oob: call __bounds_error, 0
L_ok:  return t_len
```

## 11. Consideraciones de tipado/validación que afectan al TAC

* **Índice debe ser entero**: si no, se reporta error y no se emite `INDEX_*`.
* **Compatibilidad de tipos** en escritura: `elem_type := rhs_type` debe ser válida; si no, error.
* **Uso de `this`**: sólo en métodos.
* **Propiedad válida**: `obj.f` debe existir y su tipo debe ser consistente (arreglo si hay indexación).
* **Dead code**: tras `return`, el bloque siguiente se marca inalcanzable y no se emite TAC útil.

## 12. Ejemplos integrados (extraídos de casos reales)

### Lectura y escritura con corto-circuito alrededor

```text
t3 = len v
if i<0 goto oob1
if i>=t3 goto oob1
goto ok2
oob1: call __bounds_error, 0
ok2: t2 = v[i]
r = t2
t4 = r + 4
t5 = len v
if i<0 goto oob3
if i>=t5 goto oob3
goto ok4
oob3: call __bounds_error, 0
ok4: v[i] = t4
```

### Método con acceso a arreglo de instancia

```text
f_Box_get:
enter f_Box_get, 12
t1 = this.data
t3 = len t1
if i<0 goto oob1
if i>=t3 goto oob1
goto ok2
oob1: call __bounds_error, 0
ok2: t2 = t1[i]
return t2
```

### Cadenas de propiedad + índice

```text
t2 = a.b
t3 = t2.c
t4 = len t3
if 1<0 goto oob1
if 1>=t4 goto oob1
goto ok2
oob1: call __bounds_error, 0
ok2: t3[1] = 3
```
