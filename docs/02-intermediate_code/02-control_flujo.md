# Generación de TAC para Control de Flujo en Compiscript

Este documento describe **cómo está implementada** la generación de **Three-Address Code (TAC/3AC)** para **control de flujo** en Compiscript: traducción efectiva de `if/else`, `while`, `do-while`, `for`, `switch`, manejo de **etiquetas** y **saltos**, **corto-circuito** en condiciones, `break/continue`, y **return**. Los patrones reflejan exactamente lo visto en los `.tac` de la batería de pruebas.

## 1. Convenciones efectivas

* **Etiquetas**: se generan como `Lstartk`, `Lbodyk`, `Lstepk`, `Lendk`, `Lthenk`, `Lelsek`, etc.
* **Saltos**: `goto Lx`, `if <cond> goto Lx` (y, cuando aplica, `ifFalse <cond> goto Lx` en algunas reglas canónicas).
* **Corto-circuito**: las condiciones booleanas se emiten con **saltos directos** (sin materializar 0/1), usando `visitCond(B, Ltrue, Lfalse)`.
* **Pila de bucles/switch**: cada bucle/switch empuja `(Lstart, Lend, Lcontinue)`:

  * `break` → `goto Lend`
  * `continue` → `goto Lcontinue` (en `while`: `Lstart`; en `for`: `Lstep`; en `do-while`: `Lcond`)
* **Temporales**: se usan para actualizaciones y expresiones (p.ej. `t2 = i + 1; i = t2`). El **pool de temporales** se resetea **por sentencia**.
* **Funciones/métodos**: al inicio se emite `enter f_label, frame_size`; retornos con `return`/`return place`.

## 2. Condicionales: `if`, `if-else`

### Esquema efectivo

**`if (B) S1`**

```text
Lthen = ...
Lend  = ...
visitCond(B, Lthen, Lend)
Lthen: S1.code
Lend:
```

**`if (B) S1 else S2`**

```text
Lthen = ...
Lelse = ...
Lend  = ...
visitCond(B, Lthen, Lelse)
Lthen: S1.code
       goto Lend
Lelse: S2.code
Lend:
```

### `visitCond(B, Ltrue, Lfalse)` (resumen)

* `B1 || B2`: `B1.true = Ltrue`, `B1.false = Lmid`; `B2.true = Ltrue`, `B2.false = Lfalse`
* `B1 && B2`: `B1.true = Lmid`, `B1.false = Lfalse`; `B2.true = Ltrue`, `B2.false = Lfalse`
* `E1 rel E2`:

  ```bash
  if E1 rel E2 goto Ltrue
  goto Lfalse
  ```

* `!B1`: invierte destinos: `visitCond(B1, Lfalse, Ltrue)`
* Otros (poco frecuentes): si la gramática obliga a valor 0/1, se materializa un temporal booleano y se testea.

**Ejemplo real:**

```text
if x<3||y>7&&x!=y goto Lthen1
goto Lelse3
Lthen1: x = 0
       goto Lend2
Lelse3: x = 1
Lend2:
```

## 3. Bucles

### `while (B) S`

Patrón canónico observado:

```text
Lstart1:
  if i<n goto Lbody2
  goto Lend3
Lbody2:
  ... cuerpo ...
  goto Lstart1
Lend3:
```

* **continue**: `goto Lstart1`
* **break**: `goto Lend3`

### `do { S } while (B);`

Patrón canónico observado:

```text
Lbody1:
  ... cuerpo ...
Lcond2:
  if B goto Lbody1
  goto Lend3
Lend3:
```

* **continue**: `goto Lcond2`

### `for (init; B; step) S`

El `for` se desazucara a `init` + `while` con bloque `Lstep`:

```text
; init
Lstart1:
  if B goto Lbody2
  goto Lend3
Lbody2:
  ... cuerpo ...
Lstep4:
  ; step
  goto Lstart1
Lend3:
```

* **continue**: `goto Lstep4`

**Ejemplo real (`for` azúcar)**

```text
s = 0
k = 0
Lstart1:
  if k<3 goto Lbody2
  goto Lend3
Lbody2:
  t2 = s + k
  s = t2
Lstep4:
  k = k+1
  goto Lstart1
Lend3:
```

## 4. `switch/case/default` con fall-through

* Se evalúa la expresión de control **una vez**, luego se encadenan comparaciones `==` a etiquetas de caso.
* **Fall-through** real: no se insertan `goto` implícitos entre casos.
* `break` salta a `Lend`.

**Esquema:**

```text
t_ctrl = E
if t_ctrl == k1 goto Lcase1
if t_ctrl == k2 goto Lcase2
...
goto Ldef|Lend

Lcase1: S1.code
        ; sin break → cae a siguiente

Lcase2: S2.code
        ...

Ldef:   Sd.code
Lend:
```

**Ejemplo real minimal:**

```text
op = 1
r  = 0
if op == 0 goto Lcase3
if op == 1 goto Lcase4
goto Ldef2
Lcase3: r = 10
        goto Lend1
Lcase4: r = 20
Ldef2:  t1 = r + 1
        r  = t1
Lend1:
```

## 5. `break` y `continue`

* **Pila de contexto** por bucle/switch: `(Lstart, Lend, Lcontinue)`.
* **`break`**: `goto Lend` del contexto superior.
* **`continue`**:

  * `while`: `goto Lstart`
  * `for`: `goto Lstep`
  * `do-while`: `goto Lcond`

Esto soporta **anidamiento** de bucles y `switch` sin ambigüedad.

## 6. `return`

* **Entrada**: `enter f_label, <frame_size>` (pseudo-op informativo).
* **`return;`** → `return`
* **`return E;`** → evaluar `E` si aplica y `return place`
* El **flujo termina** en el punto del `return`. Código posterior en el mismo bloque se marca **inalcanzable** en semántica (y no se emite TAC útil).

**Ejemplos reales:**

```text
f_f:
enter f_f, 0
return

f_main:
enter f_main, 0
call f_f, 0
return
```

## 7. Corto-circuito y temporales (consideraciones)

* En **condiciones** (`if`, `while`, etc.) se prefieren **saltos**: no se materializa booleano intermedio.
* En **expresiones de actualización** o fragmentos no condicionales se usan temporales aritméticos (`t = i + 1`), liberados inmediatamente tras la asignación final de la sentencia.
* La elección anterior reduce instrucciones y facilita futuras optimizaciones (propagación de copias/coalescencia).

## 8. Pseudocódigo operativo

**`emitIfElse(B, S1, S2)`**

```text
Lthen = newlabel()
Lelse = newlabel()
Lend  = newlabel()
visitCond(B, Lthen, Lelse)
label Lthen
emitBlock(S1)
emit(goto Lend)
label Lelse
emitBlock(S2)
label Lend
```

**`emitWhile(B, S)`**

```text
Lstart = newlabel()
Lbody  = newlabel()
Lend   = newlabel()
pushLoop(Lstart, Lend, Lstart)
label Lstart
visitCond(B, Lbody, Lend)
label Lbody
emitBlock(S)
emit(goto Lstart)
label Lend
popLoop()
```

**`emitSwitch(E, cases, default?)`**

```text
Lv   = newtemp(type(E))
Lend = newlabel()
emit(Lv = visit(E).place)

for (k, Lcase) in cases:
  emit(if Lv == k goto Lcase)

emit(goto defaultLabel or Lend)

for (k, Lcase, S) in cases:
  label Lcase
  emitBlock(S)     ; 'break' salta a Lend

if default?:
  label defaultLabel
  emitBlock(defaultBody)

label Lend
```

## 9. Ejemplos integrados rápidos

**`while` con actualización**

```text
Lstart1:
  if i<n goto Lbody2
  goto Lend3
Lbody2:
  t2 = s + i
  s  = t2
  t3 = i + 1
  i  = t3
  goto Lstart1
Lend3:
```

**`do-while` con `continue`**

```text
Lbody1:
  t2 = a + 2
  a  = t2
Lcond2:
  if a<5 goto Lbody1
  goto Lend3
Lend3:
```
