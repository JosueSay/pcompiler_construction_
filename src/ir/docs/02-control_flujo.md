# Generación de TAC para Control de Flujo en Compiscript

Este documento describió el diseño de generación de **Código de Tres Direcciones (TAC)** para **control de flujo** en Compiscript. Se explicó cómo se tradujo cada estructura a 3AC textual y cuádruplos, cómo se gestionaron **etiquetas**, **saltos**, **corto-circuito** en condiciones booleanas y el uso de **pilas de contexto** para `break`/`continue`.

## 1. Convenciones generales

- Se representó el control mediante **etiquetas simbólicas** `Lk` y saltos `goto`, `if ... goto`, `ifFalse ... goto`.
  **Justificación:** esta forma canónica mantuvo el IR simple, legible y fácilmente optimizable; separó decisiones de control de la evaluación de expresiones y permitió reutilizar los **esquemas DDS** de corto-circuito.

- Las **condiciones booleanas** en estructuras de control se tradujeron con el procedimiento `visitCond(B, Ltrue, Lfalse)`, que emitió saltos directamente (sin crear temporales booleanos), aplicando corto-circuito de manera determinista.

- Se gestionaron **pilas de contexto de bucle** para soportar `break` y `continue`:

  - Cada bucle empujó `(Lstart, Lend, Lcontinue)` en una pila.
  - `break` saltó a `Lend`.
  - `continue` saltó a `Lcontinue` (o a la reevaluación de condición, según el bucle).

- Donde correspondió, se usaron **temporales** para preservar el modelo 3AC (por ejemplo, en actualizaciones `i = i + 1`). No se materializaron booleanos a `0/1` dentro de condiciones de control.

**Referencias:** `docs/README_TAC_GENERATION.md`, `src/semantic/analyzers/controlFlow.py`, `src/semantic/analyzers/returns.py`, Aho et al., cap. 6–7.

## 2. Condicionales: `if`, `if-else`

### Esquema de traducción

- **`if (B) S1`**

  ```bash
  Lthen = newlabel()
  Lend  = newlabel()
  visitCond(B, Lthen, Lend)
  Lthen: S1.code
  Lend:
  ```

- **`if (B) S1 else S2`**

  ```bash
  Lthen = newlabel()
  Lelse = newlabel()
  Lend  = newlabel()
  visitCond(B, Lthen, Lelse)
  Lthen: S1.code
         goto Lend
  Lelse: S2.code
  Lend:
  ```

**Justificación:** se separaron las rutas verdadera/falsa en etiquetas, permitiendo corto-circuito en `B` y evitando temporales booleanos. Esta forma es estándar y favoreció la construcción de bloques básicos.

### Pseudocódigo `visitCond`

```text
function visitCond(B, Ltrue, Lfalse):
    match B:
        case (B1 || B2):
            Lmid = newlabel()
            visitCond(B1, Ltrue, Lmid)
            emitLabel(Lmid)
            visitCond(B2, Ltrue, Lfalse)

        case (B1 && B2):
            Lmid = newlabel()
            visitCond(B1, Lmid, Lfalse)
            emitLabel(Lmid)
            visitCond(B2, Ltrue, Lfalse)

        case (E1 relop E2):
            L = visit(E1)   ; R = visit(E2)
            emit( if L.place relop R.place goto Ltrue )
            emit( goto Lfalse )
            freeIfTemp(L); freeIfTemp(R)

        case (!B1):
            visitCond(B1, Lfalse, Ltrue)

        default:
            ; Si la gramática permitió otras formas, se materializó 0/1:
            T = visitAsBoolean(B)       ; T ∈ {0,1}
            emit( if T goto Ltrue )
            emit( goto Lfalse )
            freeIfTemp(T)
```

### Ejemplo

Código fuente:

```c
if (x < 10 || x > 20) {
  y = 0;
} else {
  y = 1;
}
```

3AC:

```bash
Lthen = ...
Lelse = ...
Lend  = ...
if x < 10 goto Lthen
ifFalse x > 20 goto Lelse
Lthen: y = 0
       goto Lend
Lelse: y = 1
Lend:
```

## 3. Bucles: `while`, `do-while`, `for`

### `while (B) S`

**Esquema:**

```bash
Lstart = newlabel()
Lbody  = newlabel()
Lend   = newlabel()
pushLoop(Lstart, Lend, Lstart) ; continue -> reevaluación
Lstart:
    visitCond(B, Lbody, Lend)
Lbody:
    S.code
    goto Lstart
Lend:
popLoop()
```

**Justificación:** `continue` saltó a `Lstart` para reevaluar `B`. Se mantuvo el patrón clásico de tres etiquetas.

### `do S while (B);`

**Esquema:**

```bash
Lstart = newlabel()
Lcond  = newlabel()
Lend   = newlabel()
pushLoop(Lcond, Lend, Lcond)
Lstart:
    S.code
Lcond:
    visitCond(B, Lstart, Lend)
Lend:
popLoop()
```

**Justificación:** `continue` saltó a `Lcond` para evaluar `B` tras el cuerpo, respetando la semántica de `do-while`.

### `for (init; B; step) S`

**Traducción determinista (C-style):**

```bash
; init
init.code

Lstart = newlabel()
Lbody  = newlabel()
Lstep  = newlabel()
Lend   = newlabel()
pushLoop(Lstart, Lend, Lstep)

Lstart:
    if B existe:
        visitCond(B, Lbody, Lend)
    else:
        goto Lbody

Lbody:
    S.code
Lstep:
    ; step
    step.code
    goto Lstart
Lend:
popLoop()
```

**Justificación:** se descompuso `for` en `init` + bucle `while` con `step` al final; `continue` apuntó a `Lstep` para ejecutar la actualización antes de reevaluar `B`.

### Ejemplo (while)

Código:

```c
while (i < n) {
  a[i] = v;
  i = i + 1;
}
```

3AC:

```bash
Lstart:
    if i < n goto Lbody
    goto Lend
Lbody:
    a[i] = v
    t1   = i + 1
    i    = t1
    goto Lstart
Lend:
```

## 4. `switch/case` y `default`

Se implementó `switch (E) { case k1: S1; case k2: S2; ... default: Sd; }` con **etiquetas por `case`** y un **salto final** `Lend`. Se respetó **fall-through** al no insertar saltos implícitos entre casos; los `break` del cuerpo cerraron el `switch` saltando a `Lend`.

**Esquema:**

```bash
Lv    = newtemp(type(E))
Lend  = newlabel()
Lcase1 = newlabel()
Lcase2 = newlabel()
...
Ldef   = newlabel()   ; si existe

; evaluar E una sola vez
V = visit(E)
emit( Lv = V.place )

; encadenar pruebas
emit( if Lv == k1 goto Lcase1 )
emit( if Lv == k2 goto Lcase2 )
...
if default existe:
    emit( goto Ldef )
else:
    emit( goto Lend )

; cuerpo de cada caso
Lcase1:  S1.code
         ; si no hubo break explícito, cae al siguiente case (fall-through)
Lcase2:  S2.code
         ...
Ldef:    Sd.code      ; si existe

Lend:
```

**Justificación:** se evaluó la expresión de control una sola vez, se emitieron pruebas en cascada con saltos a etiquetas de caso, y `break` se resolvió vía la misma pila de bucle/switch apuntando a `Lend`. Este patrón minimizó temporales y mantuvo la semántica de **fall-through**.

### Ejemplo

Código:

```c
switch (op) {
  case 0: r = a + b; break;
  case 1: r = a - b;
  default: r = 0;
}
```

3AC:

```bash
t_op = op
if t_op == 0 goto Lcase0
if t_op == 1 goto Lcase1
goto Ldef

Lcase0: t1 = a + b
        r  = t1
        goto Lend

Lcase1: t2 = a - b
        r  = t2
        ; fall-through a default

Ldef:   r  = 0
Lend:
```

## 5. `break` y `continue` dentro de bucles

Se usó una **pila de contexto** para saber los destinos de `break` y `continue` del bucle más interno:

- Al entrar a un bucle se hizo `pushLoop(Lstart, Lend, Lcontinue)`.
- `break` emitió: `goto Lend`.
- `continue` emitió: `goto Lcontinue`.

**Justificación:** la pila evitó dependencias globales, soportó anidamiento y respetó el comportamiento semántico implementado en `controlFlow.py` (que validó `break/continue` según profundidad de bucle).

### Ejemplo

Código:

```c
while (true) {
  if (x == 0) break;
  if (x % 2 == 0) { x = x - 1; continue; }
  x = x - 3;
}
```

3AC (esqueleto):

```bash
Lstart:
    if true goto Lbody
    goto Lend
Lbody:
    if x == 0 goto Lend
    if x % 2 == 0 goto Leven
    goto Lodd
Leven:
    t1 = x - 1
    x  = t1
    goto Lstart        ; continue
Lodd:
    t2 = x - 3
    x  = t2
    goto Lstart
Lend:
```

## 6. `return` dentro de funciones

Se modeló la entrada de función con `enter f_label, local_frame_size` (pseudo-op) y los retornos como:

- **`return;`**

  ```bash
  return
  ```

- **`return E;`**

  ```bash
  T = visit(E)       ; si aplica
  return T.place
  ```

El retorno terminó el flujo del bloque actual (consistente con la semántica de `returns.py` y el análisis de **código inalcanzable** en `statements.py`). El tamaño del marco (`local_frame_size`) se fijó al cerrar el ámbito de la función, de acuerdo con `ScopeManager`.

**Justificación:** la forma canónica `return [place]` simplificó la convención de llamada. El uso de `enter` permitió conservar la información de RA para el backend, sin fijar detalles de máquina en esta fase.

### Ejemplo

Código:

```c
function f(a: int, b: int): int {
  if (a > b) return a;
  return b;
}
```

3AC:

```bash
enter f, <frame_size>
if a > b goto LretA
goto LretB
LretA:
    return a
LretB:
    return b
```

## 7. Consideraciones sobre temporales y corto-circuito

- En **condiciones** de control, se empleó `visitCond` con **saltos** y **etiquetas** para implementar **corto-circuito**; no se materializó un temporal booleano, lo que evitó trabajo extra y preservó la forma estándar de 3AC.
- En **partes no condicionales** (por ejemplo, en expresiones de actualización o `for (init; cond; step)`), se emplearon temporales numéricos cuando la forma `x = y op z` lo requirió. El **reciclaje** se realizó en post-orden por sentencia, manteniendo bajo el número de temporales vivos.

**Justificación:** esta separación redujo la complejidad y permitió que los optimizadores posteriores (o el backend) apliquen coalescencia y propagación de copias si fuera conveniente.

## 8. Pseudocódigo de emisión para estructuras clave

### 8.1 `if-else`

```text
function emitIfElse(B, S1, S2):
    Lthen = newlabel()
    Lelse = newlabel()
    Lend  = newlabel()
    visitCond(B, Lthen, Lelse)
    emitLabel(Lthen)
    emitBlock(S1)
    emit( goto Lend )
    emitLabel(Lelse)
    emitBlock(S2)
    emitLabel(Lend)
```

### 8.2 `while`

```text
function emitWhile(B, S):
    Lstart = newlabel()
    Lbody  = newlabel()
    Lend   = newlabel()
    pushLoop(Lstart, Lend, Lstart)
    emitLabel(Lstart)
    visitCond(B, Lbody, Lend)
    emitLabel(Lbody)
    emitBlock(S)
    emit( goto Lstart )
    emitLabel(Lend)
    popLoop()
```

### 8.3 `switch`

```text
function emitSwitch(E, cases, defaultOpt):
    Lv   = newtemp(type(E))
    Lend = newlabel()
    emit( Lv = visit(E).place )

    for (k, Lcase) in cases:           ; casos en orden
        emit( if Lv == k goto Lcase )

    if defaultOpt exists:
        emit( goto defaultOpt.label )
    else:
        emit( goto Lend )

    for (k, Lcase, S) in cases:
        emitLabel(Lcase)
        emitBlock(S)                    ; los break internos saltan a Lend

    if defaultOpt exists:
        emitLabel(defaultOpt.label)
        emitBlock(defaultOpt.body)

    emitLabel(Lend)
```

## 9. Ejemplos integrados

### 9.1 `for` con inicialización, condición y actualización

Código:

```c
for (i = 0; i < n; i = i + 1) {
  sum = sum + a[i];
}
```

3AC:

```bash
i  = 0
Lstart:
    if i < n goto Lbody
    goto Lend
Lbody:
    t1 = a[i]
    t2 = sum + t1
    sum = t2
Lstep:
    t3 = i + 1
    i  = t3
    goto Lstart
Lend:
```

### 9.2 `do-while` con `continue`

Código:

```c
do {
  x = x - 1;
  if (x % 2 == 0) continue;
  y = y + x;
} while (x > 0);
```

3AC:

```bash
Lstart:
    t1 = x - 1
    x  = t1
    if x % 2 == 0 goto Lcond        ; continue
    t2 = y + x
    y  = t2
Lcond:
    if x > 0 goto Lstart
    goto Lend
Lend:
```
