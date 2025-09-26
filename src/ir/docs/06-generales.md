# Generación de TAC para Reglas Generales en Compiscript

Este documento describió el diseño de **generación de Código de Tres Direcciones (TAC, Three-Address Code)** para las **reglas generales** del lenguaje Compiscript. Se explicó cómo se reflejaron en TAC la **detección de código muerto**, la **validación semántica previa** de expresiones, el **manejo de declaraciones duplicadas**, y las **estrategias de temporales, etiquetas y control de flujo** que sustentaron estos casos.

## 1. Detección de código muerto y reflejo en TAC

### 1.1 Señales semánticas de terminación

El análisis semántico marcó terminación de flujo para:

- `return` (en `analyzers/returns.py`),
- `break`/`continue` fuera del contexto permitido (error),
- y, dentro de `statements.py`/`controlFlow.py`, la variable interna de estado indicó que un **statement acabó el flujo** del bloque (por ejemplo, un `return` en medio de un bloque).

Estas señales se propagaron al emisor TAC como **barreras de emisión**: a partir del punto en que el flujo se consideró terminado, **no se emitieron** cuádruplos adicionales dentro del mismo bloque léxico.

### 1.2 Política de emisión en regiones muertas

- En regiones marcadas como **muertas** se suprimió la generación de:

  - nuevos **temporales**,
  - nuevas **etiquetas**,
  - y nuevas **instrucciones**.
- Se permitió, no obstante, cerrar estructuras ya abiertas (p. ej., emitir la **etiqueta** de salida de un `if-else` o de un bucle si había sido reservada antes del punto de terminación), para mantener el **3AC textual** bien formado.

**Justificación.** Conservar la integridad del flujo a nivel de etiquetas evitó inconsistencias en el **3AC textual** y en los cuádruplos, al tiempo que reflejó fielmente la **semántica de inalcanzabilidad**.

### 1.3 Ejemplo — código muerto tras `return`

Código:

```c
function f(a: int): int {
  return a;
  a = a + 1; // muerto
}
```

TAC:

```bash
f_f:
enter f_f, <frame>
return a
; no se emitió ninguna instrucción para "a = a + 1"
```

El caso se correspondió con `src/test/generales/error_codigo_muerto_return.cps` en el ámbito de pruebas.

### 1.4 Ejemplo — código muerto tras `break`

Código:

```c
while (true) {
  break;
  x = 1; // muerto
}
```

TAC:

```bash
Lstart:
    if true goto Lbody
    goto Lend
Lbody:
    goto Lend        ; break
Lend:
```

No se emitió `x = 1`.

## 2. Validación de expresiones semánticamente válidas y garantía en TAC

### 2.1 Validación en semántica, supresión en TAC

La verificación de expresiones bien tipadas se realizó en **semántica** (`expressions.py`, `lvalues.py`, `type_system.py`). Por ejemplo, no se permitió multiplicar **funciones** o aplicar operadores a **referencias no compatibles**. Cuando se detectó un error:

- **no se materializó** el `place` de la expresión,
- el **emisor TAC** recibió un valor vacío/erróneo y **suprimió** la emisión de la instrucción, registrándose el diagnóstico en `diagnostics.py`.

**Justificación.** La fase TAC asumió una **entrada tipada**. Evitar emisiones parciales impidió cuádruplos inconsistentes (p. ej., `t = f * 2` donde `f` es una función).

### 2.2 Ejemplo — expresión inválida (no emisión)

Código:

```c
function g(): void {}
let x = g * 2; // inválido: "g" es una función
```

TAC (fragmento):

```bash
; no se emitió "t = g * 2" por error semántico
; el resto del bloque, si fue válido, sí se emitió
```

La **consistencia** del bloque se mantuvo; el diagnóstico quedó en logs y el 3AC permaneció ejecutable para las partes válidas.

## 3. Declaraciones duplicadas y consistencia de la tabla de símbolos

### 3.1 Rechazo de duplicados en el mismo scope

`symbol_table.py` y `scope_manager.py` rechazaron **declaraciones duplicadas** en el mismo ámbito (variables o parámetros). En ese caso:

- El emisor **no** reservó espacio duplicado,
- No se emitieron inicializaciones redundantes,
- Se conservó el símbolo **previo** como el único válido del scope.

### 3.2 Sombras (shadowing) en scopes internos

Se permitió **shadowing** en scopes internos, produciendo **símbolos distintos** con `storage` y `offset` propios. El emisor TAC:

- Usó el **símbolo resuelto** por el `scope_manager` para cada **l-value**,
- Empleó direcciones lógicas consistentes (global/stack/param + offset) según los campos del símbolo.

**Justificación.** Al respetar las reglas de la tabla de símbolos, el TAC no introdujo ambigüedades ni "dobles escrituras" y mantuvo el **mapeo 1:1** entre nombre visible y **ubicación**.

### 3.3 Ejemplo — duplicado en mismo scope (no emisión de segunda reserva)

Código:

```c
let a: int = 1;
let a: int = 2; // duplicado, error
```

TAC:

```bash
a = 1
; no se emitió "a = 2" ni reserva nueva para "a"
```

### 3.4 Ejemplo — shadowing en scope interno

Código:

```c
let a: int = 1;
{
  let a: int = 2; // sombra
  x = a;          // usa el interno
}
y = a;            // usa el externo
```

TAC (esqueleto):

```bash
a   = 1
; entrar a bloque: símbolo 'a' (interno) con offset diferente
a#1 = 2             ; conceptual: dirección distinta (stack offset)
x   = a#1
; salir de bloque
y   = a             ; el externo
```

En el 3AC textual se representó con el mismo lexema `a`, pero el **resolutor de símbolos** estableció diferentes ubicaciones lógicas; los cuádruplos internos apuntaron al `offset` del símbolo interno.

## 4. Estrategias de temporales, etiquetas y control de flujo

### 4.1 Temporales

- Se empleó un **pool de temporales por función**, aislado entre funciones/procedimientos.
- Se recicló en **post-orden por sentencia**. Al suprimir la emisión por error o por código muerto, se **liberaron** temporales evaluados previamente que no se usaron.
- No se reutilizaron **identificadores de temporales** entre funciones (espacio de nombres por función), evitando colisiones semánticas.

### 4.2 Etiquetas

- Se generaron etiquetas (`Lk`) de forma **monótona**.
- En presencia de **código muerto** posterior a una etiqueta ya emitida, **no** se generaron **nuevas etiquetas** innecesarias; se cerró el bloque actual y se continuó con la siguiente estructura válida.

### 4.3 Control de flujo

- Las condiciones se tradujeron con **corto-circuito** y **saltos** (`if ... goto`, `ifFalse ... goto`), sin materializar booleanos intermedios salvo en contextos de valor.
- Para `break`/`continue`, se usó una **pila de contextos** para resolver destinos (`Lend`, `Lstep`/`Lstart`), y se propagó el estado de **terminación de flujo** al emisor.

**Justificación.** Estas estrategias mantuvieron **determinismo** y **compacidad** del 3AC, y sostuvieron la coherencia con la semántica de finalización de bloques y verificación de alcance.

## 5. Justificación unificada de diseño

1. **Separación de responsabilidades.** La **validación semántica** (tipos, existencia, contextos) se realizó antes de la generación de TAC. El emisor trabajó con **entradas ya validadas**, suprimió emisiones ante errores y mantuvo el 3AC **coherente y ejecutable** para las porciones válidas.
2. **Reflejo fiel de la inalcanzabilidad.** Suprimir emisión en **regiones muertas** hizo que el TAC coincidiera con el flujo real, simplificando análisis posteriores (liveness, construcción de CFG) y cumpliendo la expectativa de la rúbrica (`docs/README_TAC_GENERATION.md`).
3. **Consistencia con la tabla de símbolos.** Respetar `storage`, `offset`, `width`, `scope_id` y la política de duplicados/shadowing aseguró que el TAC refiriera **ubicaciones correctas** y no produjera estados inconsistentes.
4. **Economía de temporales y etiquetas.** El reciclaje local y el control de etiquetas mantuvieron el IR compacto, legible y **estable** ante optimizaciones, sin fugas entre funciones ni distorsiones por errores locales.

## 6. Pseudocódigo de emisión (resumen)

### 6.1 Barrera de emisión por terminación de flujo

```text
function emitStmt(S):
    if currentBlock.terminated: 
        return  ; suprimir emisión en región muerta
    R = analyzeAndMaybeEmit(S)
    if R.terminates:
        currentBlock.terminated = true
```

### 6.2 Emisión de expresión con validación previa

```text
function emitExpr(E):
    if E.hasSemanticError:
        return None  ; no emitir, no crear temporales
    R = translateToPlace(E)  ; genera TAC si es necesario
    return R
```

### 6.3 Manejo de duplicados

```text
function declareSymbol(name, type):
    if currentScope.contains(name):
        diagnostics.error("duplicated declaration")
        return None
    sym = currentScope.add(name, type, storage, offset, width)
    return sym
```

## 7. Ejemplos integrados

### 7.1 Mezcla de retorno temprano y código posterior

Código:

```c
function abs(a: int): int {
  if (a >= 0) return a;
  let b: int = -a;
  return b;
  b = b + 1; // muerto
}
```

TAC:

```bash
f_abs:
enter f_abs, <frame>
if a >= 0 goto LretA
goto Lcont
LretA:
    return a
Lcont:
    t1 = - a
    b  = t1
    return b
; sin emisión para "b = b + 1"
```

### 7.2 Duplicado de parámetro (no emisión adicional)

Código:

```c
function f(x: int, x: int): void { } // error semántico
```

TAC:

```bash
f_f:
enter f_f, <frame>
return
; sin redefinición ni reservas duplicadas para "x"
```

### 7.3 Expresión inválida suprimida y continuación del bloque

Código:

```c
function h(): void {
  let y: int = 0;
  y = print * 2; // inválido si 'print' no es valor numérico
  y = 3;         // válido
}
```

TAC:

```bash
f_h:
enter f_h, <frame>
y = 0
; sin emisión para "y = print * 2"
y = 3
return
```
