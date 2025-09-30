# Generación de TAC para Reglas Generales

Este documento explica cómo se reflejan en el **Three-Address Code (TAC/3AC)** las **reglas generales** de Compiscript: detección de **código muerto**, relación con la **validación semántica previa**, manejo de **declaraciones duplicadas** y las estrategias de **temporales, etiquetas y control de flujo** que sostienen estos comportamientos.

## 1. Detección de código muerto y su reflejo en TAC

### 1.1 Señales de terminación desde semántica

El análisis semántico marca fin de flujo cuando aparece, por ejemplo, un `return`. Esa señal se propaga al emisor como **barrera**: desde ese punto, **no se emite** TAC adicional dentro del mismo bloque léxico.

### 1.2 Política en regiones muertas

* En regiones muertas se **suprime** la creación de temporales, etiquetas e instrucciones.
* Solo se permiten las **etiquetas de cierre** necesarias (si ya estaban reservadas) para mantener un 3AC bien formado.

**Motivo**: reflejar fielmente la inalcanzabilidad y evitar inconsistencias en el IR.

### 1.3 Ejemplo — muerto tras `return`

Fuente:

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
; sin emisión para "a = a + 1"
```

### 1.4 Ejemplo — muerto tras `break`

Fuente:

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

## 2. Validación semántica previa y garantía en TAC

### 2.1 Semántica valida, TAC asume

La tipificación y los usos válidos de expresiones/lvalues se comprueban en **semántica**. Si hay error:

* No se materializa un `place`.
* El emisor **no** genera la instrucción de esa expresión.
* Se conserva el resto del bloque válido.

### 2.2 Ejemplo — expresión inválida (no emisión)

Fuente:

```c
function g(): void {}
let x = g * 2; // inválido si 'g' no es valor numérico
```

TAC (fragmento):

```bash
; sin "t = g * 2"
; el resto del bloque válido sí se emite
```

## 3. Declaraciones duplicadas y tabla de símbolos

### 3.1 Duplicados en el mismo scope

Los duplicados se **rechazan**. Consecuencias:

* No hay reserva duplicada.
* No hay inicialización redundante.
* Se mantiene el símbolo previamente válido.

Ejemplo:

```c
let a: int = 1;
let a: int = 2; // duplicado
```

TAC:

```bash
a = 1
; sin "a = 2" ni reservas extra
```

### 3.2 Shadowing en scopes internos

Se permite sombreado; cada símbolo tiene su propia ubicación lógica (global/stack/param + offset). El emisor usa **el símbolo resuelto** por el gestor de scopes en cada uso.

Ejemplo:

```c
let a: int = 1;
{
  let a: int = 2; // sombra
  x = a;          // interno
}
y = a;            // externo
```

TAC (esqueleto):

```bash
a   = 1
; bloque interno: 'a' interno con offset distinto
a#1 = 2
x   = a#1
; fuera del bloque
y   = a
```

## 4. Estrategias de temporales, etiquetas y control de flujo

### 4.1 Temporales

* **Pool por función** (aislado entre funciones/métodos).
* Reciclaje **por sentencia** (post-orden).
* Ante error o región muerta, se liberan los temporales ya evaluados que no se usan.

### 4.2 Etiquetas

* Generación **monótona** de `Lk`.
* En regiones muertas no se crean etiquetas nuevas innecesarias; solo se cierran bloques si era requerido.

### 4.3 Control de flujo

* Condiciones con **corto-circuito** vía `if ... goto`/`ifFalse ... goto` (sin materializar booleanos salvo en contextos de valor).
* `break`/`continue` resueltos con **pila de contextos** de bucle/switch (destinos `Lend`, `Lstep`/`Lstart`).

## 5. Justificación unificada

1. **Separación de responsabilidades**: semántica valida; TAC emite solo sobre entrada correcta y **suprime** emisiones inválidas.
2. **Fidelidad del flujo**: las barreras por terminación hacen que el IR refleje exactamente lo ejecutable, simplificando CFG/analizadores posteriores.
3. **Consistencia con símbolos**: uso de `storage/offset/scope_id` evita ambigüedades y dobles escrituras.
4. **Economía de IR**: reciclaje de temporales y prudencia con etiquetas mantienen 3AC compacto y estable.

## 6. Pseudocódigo (resumen)

### 6.1 Barrera de emisión

```text
emitStmt(S):
  if currentBlock.terminated:
      return
  R = analyzeAndMaybeEmit(S)
  if R.terminates:
      currentBlock.terminated = true
```

### 6.2 Emisión de expresión con validación previa

```text
emitExpr(E):
  if E.hasSemanticError:
      return None
  return translateToPlace(E)
```

### 6.3 Declaración con detección de duplicados

```text
declareSymbol(name, type):
  if currentScope.contains(name):
      error("duplicated declaration")
      return None
  return currentScope.add(name, type, storage, offset, width)
```

## 7. Ejemplos integrados

### 7.1 Retorno temprano y código posterior muerto

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
; sin emisión para código tras el segundo return
```

### 7.2 Duplicado de parámetro (suprimido)

```bash
f_f:
enter f_f, <frame>
return
; sin redefinir "x" ni reservar dos veces
```

### 7.3 Expresión inválida suprimida y continuación del bloque

```bash
f_h:
enter f_h, <frame>
y = 0
; sin emisión para "y = print * 2" si es inválido
y = 3
return
```
