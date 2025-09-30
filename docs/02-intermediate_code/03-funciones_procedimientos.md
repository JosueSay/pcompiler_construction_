# Generación de TAC para Funciones y Procedimientos

Este documento resume **cómo está implementada** la generación de **Three-Address Code (TAC/3AC)** para **funciones, procedimientos y métodos** (incluyendo constructores), **llamadas**, **retornos**, **recursión y closures**, manejo de **parámetros/locales**, y el **modelo lógico de registros de activación (RA)**. Los ejemplos reflejan los `.tac` generados por la batería de pruebas.

## 1. Convenciones del IR

* **Dos vistas**:

  * **3AC textual** (ficheros `.tac`) con etiquetas y pseudo-op `enter`.
  * **Cuádruplos** `(op, arg1, arg2, res)` mantenidos en memoria.
* **Visitas de expresión** devuelven `ExprRes{ type, place, is_temp }` y emiten efectos **in situ** con un `Emitter` compartido.
* **Temporales**: pool **por función**, reciclaje **por sentencia** (post-orden). Los nombres de temporales se **reutilizan dentro de la función**, pero **no** entre funciones (espacios de nombres independientes).
* **Protocolo de llamada**: `param <arg>` (L→R), `t = call f_label, n` (si hay retorno) o `call f_label, n` (void).
* **Entrada de función**: `enter f_label, <local_frame_size>`. El epílogo se modela con `return [place]`.

## 2. Símbolos y metadatos de función/método

Cada función/método se registra con:

* `label` de entrada (`f_<name>` o `f_<Clase>_<método>`).
* `param_types`, `return_type`.
* `local_frame_size` (obtenido al cerrar el scope con `ScopeManager`).
* `captures_layout` si hay **closures** (orden y tipos de capturas).

Esto permite enlazar `call` por etiqueta, verificar tipos en semántica y fijar el RA.

## 3. Definiciones: forma emitida

```bash
f_<name>:
enter f_<name>, <local_frame_size>
; cuerpo (puede tener múltiples return)
```

* No se requiere un `return` sintético final si ya se retornó en todos los caminos (semántica garantiza exhaustividad en no-void).
* Para **métodos**, `this` está disponible como identificador en el cuerpo (ver §7).

**Ejemplo real (suma):**

```bash
f_add:
enter f_add, 8
t1 = a + b
return t1
```

## 4. Llamadas y evaluación de argumentos

* **Orden**: izquierda → derecha.
* Por cada argumento materializado: `param <place>`.
* **Con retorno**: `t = call f_label, arity` y luego asignación a la variable destino si aplica.
* **Sin retorno**: `call f_label, arity`.

**Ejemplo real:**

```bash
t1 = u + 1
param t1
param v
t2 = call f_add, 2
r  = t2
```

## 5. `return` y validación semántica

* **`return E;`** → evaluar `E` y `return <place>`.
* **`return;`** → `return` (void).
* Semántica aplica:

  * Coincidencia de tipo de retorno con `return_type`.
  * Marcado de **terminación de flujo** (diagnóstico de código inalcanzable).

**Ejemplo real (máximo):**

```bash
f_max:
enter f_max, <frame>
if a>b goto LretA
goto LretB
LretA:
  return a
LretB:
  return b
```

## 6. Recursión

No requiere manejo especial en TAC: la función se invoca por su `label`.

**Ejemplo real (factorial):**

```bash
f_fact:
enter f_fact, 4
if n<=1 goto Lthen1
goto Lend2
Lthen1:
  return 1
Lend2:
  t2 = n - 1
  param t2
  t3 = call f_fact, 1
  t4 = n * t3
  return t4
```

## 7. Métodos, `this` y constructores

* Los **métodos** usan etiqueta `f_<Clase>_<método>` y acceden a campos vía `this.campo`.
* `this` se modela como **parámetro implícito** disponible en el cuerpo.
* Los **constructores** se modelan como métodos `f_<Clase>_constructor` y se invocan explícitamente tras `newobj`.

**Ejemplos reales:**

**Método y acceso a campo:**

```bash
f_Box_get:
enter f_Box_get, 12
t1 = this.data
t3 = len t1
if i<0 goto oob1
if i>=t3 goto oob1
goto ok2
oob1: call __bounds_error, 0
ok2:
t2 = t1[i]
return t2
```

**Construcción e invocación:**

```bash
t1 = newobj Box, 8
param t1
call f_Box_constructor, 1
b = t1

param b
param 1
t2 = call f_Box_get, 2
z  = t2
```

**Método que muta un campo:**

```bash
f_Counter_inc:
enter f_Counter_inc, 8
t1 = this.x
t2 = t1 + 1
this.x = t2
return
```

## 8. Closures y funciones anidadas

Cuando una función interna captura variables externas, se materializa:

1. **Entorno**: `ENV = mkenv <capturas>` (orden según `captures_layout`).
2. **Closure**: `C = mkclos f_inner_label, ENV`.
3. **Llamada**: `t = callc C, n` (pasa env implícitamente).

**Ejemplo real (closure simple):**

```bash
f_mk:
enter f_mk, 4
base = 10
f_add:
enter f_add, 4
t1 = base + n
return t1
t2 = mkenv base
t3 = mkclos f_add, t2
param 5
t1 = callc t3, 1
return t1
```

## 9. Parámetros y locales

* **Parámetros**: por valor (`param`), con clase de almacenamiento `param`.
* **Locales**: almacenados en el **marco** (`stack`); referencias nulas por defecto si aplica.
* La **tabla de símbolos** conserva `storage ∈ {global, stack, param}`, `offset/frame_index`.
  El TAC trabaja con **lugares abstractos** (nombres, temporales, literales).

## 10. Registros de activación (RA) y pila de llamadas

Modelo lógico, independiente de máquina:

```bash
[ ret_addr | dynamic_link | static_link? | params | locals (frame_size) ]
```

* **Prólogo**: `enter f_label, local_frame_size` (anota el tamaño del marco).
* **Ejecución**: uso de `param` / `call` / `callc`.
* **Retorno**: `return [place]` (epílogo implícito).

Este modelado deja al backend la materialización real (base+desplazamiento, enlaces, etc.).

## 11 Aislamiento y reciclaje de temporales

* Pool **por función**; reseteo **por sentencia**.
* No hay colisión de `t1` entre funciones distintas.
* Los temporales previos a un `call` del **caller** siguen válidos después de la llamada; el **callee** usa su propio pool.

## 12 Patrones de emisión (pseudocódigo)

**Definición:**

```bash
emitFunction(sym_f):
  label sym_f.label
  emit enter sym_f.label, sym_f.local_frame_size
  initTempPool()
  emitBlock(body)       ; múltiples return dentro
  destroyTempPool()
```

**Llamada:**

```bash
emitCall(f_label, args, hasRet, retTy):
  for arg in args (L→R):
    A = visit(arg); emit param A.place; freeIfTemp(A)
  if hasRet:
    T = newtemp(retTy)
    emit T = call f_label, len(args)
    return T
  else:
    emit call f_label, len(args)
```

**Return:**

```bash
emitReturn(expr?):
  if expr:
    R = visit(expr)
    emit return R.place
    freeIfTemp(R)
  else:
    emit return
```

**Closure:**

```bash
ENV = mkenv(capturas...)
C   = mkclos f_inner, ENV
T   = callc C, n
```

## 13. Muestras integradas

**Función con locales:**

```bash
f_inc:
enter f_inc, <frame>
t1 = x + 1
y  = t1
return y

param a
t2 = call f_inc, 1
z  = t2
```

**Void con múltiples retornos:**

```bash
f_logTwice:
enter f_logTwice, 4
return
m = 8
param m
call f_logTwice, 1
```

> Nota: El retorno termina el flujo del bloque; cualquier TAC posterior en el mismo bloque no se ejecuta (semántica reporta “código inalcanzable” cuando aplica).
