# Generación de TAC para Listas y Estructuras de Datos

Este documento explica **cómo está implementada** la generación de **Three-Address Code (TAC/3AC)** para **listas** y estructuras relacionadas (incluyendo campos de objetos que contienen listas): **construcción**, **acceso**, **asignación**, **longitud** y **validaciones de índice**, además del manejo de **temporales** y las decisiones de diseño que lo sustentan.

## 1. Modelo y convenciones del IR

* **Dos vistas del IR**

  * **3AC textual** (`.tac`) con etiquetas (`Lk:`) y pseudo-ops (`len`, `newlist`).
  * **Cuádruplos** en memoria `(op, arg1, arg2, res)` para pruebas/opt.
* **Resultados de visita**: `ExprRes = { type, place, is_temp }`. La emisión se hace **in situ** vía `Emitter`.
* **Pool de temporales por función** con reciclaje **por sentencia** (post-orden).
* **Operaciones abstractas de lista** en TAC:

  * Construcción: `t = newlist n` + `t[k] = vk`
  * Longitud: `tL = len a`
  * Lectura: `t = a[i]`
  * Escritura: `a[i] = v`

**Motivación**: mantener el IR **independiente del layout físico** (cabecera/área de datos), delegando al backend la materialización de direcciones y tamaños.

## 2. Tipado y homogeneidad

* La **semántica** valida homogeneidad de literales `[...]`, tipos de elementos (`ArrayType(T)`) y compatibilidad en `a[i] = expr`.
* El generador TAC asume entradas **bien tipadas**; no introduce casts adicionales (más allá de las promociones numéricas previstas).

**Efecto**: el **tipo de elemento** determina los temporales en lecturas/escrituras y simplifica el IR.

## 3. Validación de índices

### 3.1 Índice entero

* La semántica exige que `i` sea entero; TAC **no** convierte tipos del índice.

### 3.2 Bounds checking (en TAC)

Para **toda** lectura/escritura indexada se emite:

```bash
tL = len A
if i < 0    goto L_oob
if i >= tL  goto L_oob
goto L_ok
L_oob: call __bounds_error, 0
L_ok:  ; operación indexada
```

**Motivación**: seguridad uniforme en IR; el backend puede mantener/optimizar/eliminar checks por configuración (debug/release).

## 4. Traducción a TAC

### 4.1 Lectura `x = a[i]`

```bash
tL = len a
if i<0 goto oob
if i>=tL goto oob
goto ok
oob: call __bounds_error, 0
ok:  tV = a[i]
x  = tV
```

### 4.2 Escritura `a[i] = v`

```bash
tL = len a
if i<0 goto oob
if i>=tL goto oob
goto ok
oob: call __bounds_error, 0
ok:  a[i] = v
```

### 4.3 Acceso mixto `obj.f[i]`

Se compone **campo → índice**:

```bash
tF = obj.f             ; FIELD_LOAD abstracto
tL = len tF
...
tV = tF[i]             ; o tF[i] = v
```

## 5. Accesos encadenados

### 5.1 Lectura doble `x = m[i][j]`

```bash
tLm = len m
check i in [0, tLm)
tRow = m[i]

tLr = len tRow
check j in [0, tLr)
tVal = tRow[j]
x    = tVal
```

### 5.2 Escritura doble `m[i][j] = v`

Mismo patrón; el último paso es **almacenamiento**.

## 6. Construcción de literales

Literal `[e1, …, en]`:

```bash
t = newlist n
t[0] = e1
...
t[n-1] = en
; valor del literal = t
```

* Evaluación **izq→der**; temporales liberados tras cada escritura.

## 7. Modelo de memoria (abstracto)

* `newlist n` produce una referencia a un bloque (cabecera con `len`, región de datos).
* `len a` lee la longitud desde la cabecera.
* `a[i]` / `a[i] = v` son operaciones **indexadas abstractas**.
* El backend baja a `base + i * elemSize`, usando tamaños/alineación del sistema de tipos.

## 8. Temporales

* **Por función** (o método), reciclaje **por sentencia**.
* En listas suelen aparecer: índice(s) `tI`, longitud `tL`, valor `tV`, campo `tF`.
* Tras cada operación se liberan los temporales que no “suben” como `place`.

## 9. Pseudocódigo esencial

**Lectura:**

```text
emitLoadIndex(aExpr, iExpr, outVar):
  A = visit(aExpr); I = visit(iExpr)
  TL = newtemp(int); emit(TL = len A.place)
  emit(if I.place < 0 goto L_oob)
  emit(if I.place >= TL goto L_oob)
  emit(goto L_ok)
  emitLabel(L_oob); emit(call __bounds_error, 0)
  emitLabel(L_ok)
  TV = newtemp(elemTypeOf(A.type))
  emit(TV = A.place[I.place])
  emit(outVar = TV)
  free(A, I, TL, TV)
```

**Escritura:**

```text
emitStoreIndex(aExpr, iExpr, vExpr):
  A = visit(aExpr); I = visit(iExpr); V = visit(vExpr)
  TL = newtemp(int); emit(TL = len A.place)
  emit(if I.place < 0 goto L_oob)
  emit(if I.place >= TL goto L_oob)
  emit(goto L_ok)
  emitLabel(L_oob); emit(call __bounds_error, 0)
  emitLabel(L_ok)
  emit(A.place[I.place] = V.place)
  free(A, I, V, TL)
```

**Campo + índice:**

```text
emitFieldIndex(objExpr, field, iExpr, outVar):
  O = visit(objExpr)
  TF = newtemp(typeOfField(O.type, field))
  emit(TF = O.place.field)
  emitLoadIndex(TF, iExpr, outVar)
  free(O, TF)
```

## 10. Ejemplos (extraídos del comportamiento real)

### 10.1 Lectura y escritura simples

```bash
t1 = newlist 3
t1[0] = 10
t1[1] = 20
t1[2] = 30
a = t1

tL = len a
if 1<0 goto oob1
if 1>=tL goto oob1
goto ok1
oob1: call __bounds_error, 0
ok1:  t2 = a[1]
x  = t2

t3 = x + 5
tL2 = len a
if 2<0 goto oob2
if 2>=tL2 goto oob2
goto ok2
oob2: call __bounds_error, 0
ok2:  a[2] = t3
```

### 10.2 Campo lista + indexación

```bash
t1 = this.data
t2 = len t1
if i<0 goto oob1
if i>=t2 goto oob1
goto ok2
oob1: call __bounds_error, 0
ok2:  t1[i] = v
```

### 10.3 Casos de error (detectados)

* **Índice negativo** → `__bounds_error`
* **Índice ≥ len** → `__bounds_error`
* **Índice no entero / tipo incompatible en asignación** → rechazado en **semántica** (no se emite TAC de la operación).
