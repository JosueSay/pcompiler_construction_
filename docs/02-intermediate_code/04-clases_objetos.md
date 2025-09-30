# Generación de TAC para Clases y Objetos

Este documento describe **cómo está implementada** la generación de **Three-Address Code (TAC/3AC)** para **clases, objetos, campos y métodos**: accesos y asignaciones a atributos, llamadas a método, construcción (`new` + constructor), uso de `this`, herencia/override (despacho estático), manejo de **temporales** y relaciones con la **tabla de símbolos** (`field_offsets`) y el **RA**.

## 1. Convenciones del IR

* **Dos vistas del IR**

  * **3AC textual** (`.tac`) con etiquetas, `enter` y operaciones de alto nivel (`FIELD_LOAD/STORE` abstractos reflejados como `obj.f` / `obj.f = ...`, e `INDEX_*` para arreglos).
  * **Cuádruplos** `(op, arg1, arg2, res)` en memoria para pruebas/opt.

* **Abstracciones clave**

  * **Campo como l-valor/expresión**: `t = obj.f` y `obj.f = v` (el offset real proviene de `field_offsets` del `ClassHandler`; el TAC **no** se acopla al layout físico).
  * **Método**: llamada con `this` implícito, etiqueta `f_<Clase>_<método>`.
  * **Temporales**: pool **por método/función**, reciclaje **por sentencia**.

## 2. Acceso a atributos

### Lectura

```bash
t1 = obj.f
x  = t1
```

### Escritura

```bash
obj.f = v
```

**Reglas de emisión:**

1. Se evalúa `obj` a un `place`.
2. Lectura: `t = obj.f` y (si aplica) copia al destino.
3. Escritura: evaluación de `v` y `obj.f = <place(v)>`.
4. Los offsets de campo quedan en `field_offsets`; el TAC mantiene `obj.f` como forma abstracta.

**Ejemplo real (de tests):**

```bash
t2 = o.x
y  = t2
t3 = y + 2
o.x = t3
```

## 3. Llamadas a métodos

**Forma con retorno:**

```bash
param obj           ; this
param a1
...
param an
tret = call f_Class_method, n+1
```

**Forma sin retorno:**

```bash
param obj
param a1
...
param an
call f_Class_method, n+1
```

**Reglas:**

* Evaluación de `obj` y argumentos **izq→der**.
* `this` siempre es el **primer** `param`.
* La **etiqueta** se resuelve estáticamente: `f_<Clase>_<método>` según el tipo estático del receptor (devirtualización cuando es conocida la clase).

**Ejemplo real:**

```bash
param b
param 1
t2 = call f_Box_get, 2
z  = t2
```

## 4. Construcción e inicialización (`new` + constructor)

**Patrón emitido:**

```bash
t_obj = newobj C, <size(C)>
param t_obj
param a1
...
param an
call f_C_constructor, n+1       ; si hay constructor
```

**Reglas:**

* `newobj` reserva espacio lógico para los campos (tamaño desde `ClassHandler` / `type_system`).
* Si existe constructor, se invoca con `this = t_obj`.
* Si no existe, se asumen **defaults** definidos por la semántica (referencias `null`, numéricos/booleanos según política del proyecto).
* El valor de la expresión `new C(...)` es `t_obj`.

**Ejemplo real:**

```bash
t4 = newobj Box, 8
param t4
param 4
call f_Box_constructor, 2
b = t4
```

## 5. Uso de `this` en métodos

`this` es un **parámetro implícito** disponible en el cuerpo.

**Ejemplos reales:**

```bash
f_Counter_inc:
enter f_Counter_inc, 8
t1 = this.x
t2 = t1 + 1
this.x = t2
return
```

```bash
f_Box_get:
enter f_Box_get, 12
t1 = this.data
...  ; checks e indexación
return t2
```

## 6. Herencia y override (despacho estático)

* Las clases registran atributos y métodos; los **offsets** de campos se consolidan en `field_offsets`.
* La resolución de llamadas usa el **tipo estático** del receptor; si el receptor es de tipo `B` y `B` hace override de `m`, se llama `f_B_m`.

**Ejemplo real:**

```bash
param b
t4 = call f_B_get, 1
r2 = t4
```

> Si más adelante se necesitara **despacho dinámico** sobre tipos base, el backend o una pasada posterior podría reescribir a `vcall`/tablas de métodos. El TAC actual permanece independiente de esa decisión.

## 7. Campos con arreglos y bounds-checks

Las lecturas/escrituras de **arreglos en campos** siguen el patrón: `FIELD_LOAD` (abstracto) → `INDEX_*` + **checks**.

**Ejemplos reales:**

```bash
f_Box_put:
enter f_Box_put, 16
t1 = this.data
t2 = len t1
if i<0 goto oob1
if i>=t2 goto oob1
goto ok2
oob1: call __bounds_error, 0
ok2:
t1[i] = v
return
```

```bash
f_Box_get:
enter f_Box_get, 12
t1 = this.data
t3 = len t1
if i<0 goto oob3
if i>=t3 goto oob3
goto ok4
oob3: call __bounds_error, 0
ok4:
t2 = t1[i]
return t2
```

**Para propiedades encadenadas** (p. ej., `a.b.c[i] = v`) se encadenan cargas de campo hasta obtener el arreglo, se emite el **bounds-check** y luego el `INDEX_STORE`.

## 8. Scopes, RA y símbolos

* Los **métodos** abren su propio **marco**: `enter f_Class_method, <frame>`.
* `this` se inserta en el scope del método con tipo `ClassType(C)`.
* `ClassHandler` registra **atributos** (tipo y offset) y valida accesos; la semántica aseguró firmas y tipos de métodos.
* El TAC permanece **abstracto**: `obj.f` y `a[i]` sin bajar a aritmética de direcciones; eso queda para el backend.

## 9. Temporales y reciclaje

* Pool **por método**; reciclaje **por sentencia**.
* Los temporales producidos al evaluar argumentos se **liberan** tras `param`, salvo que el valor deba reutilizarse.
* No hay colisiones de `t1` entre funciones/métodos distintos.

## 10. Pseudocódigo (esenciales)

**Lectura/escritura de campo:**

```text
emitFieldLoad(obj, f):
  O = visit(obj)
  T = newtemp(typeOfField(O.type, f))
  emit( T = O.place.f )
  freeIfTemp(O)
  return T

emitFieldStore(obj, f, val):
  O = visit(obj); V = visit(val)
  emit( O.place.f = V.place )
  freeIfTemp(O); freeIfTemp(V)
```

**Llamada a método:**

```text
emitMethodCall(obj, m, args, retTy?):
  O = visit(obj)
  emit( param O.place )
  for a in args:
    A = visit(a); emit( param A.place ); freeIfTemp(A)
  if retTy:
    T = newtemp(retTy)
    emit( T = call f_<Class>_<m>, len(args)+1 )
    freeIfTemp(O)
    return T
  else:
    emit( call f_<Class>_<m>, len(args)+1 )
    freeIfTemp(O)
```

**Construcción:**

```text
emitNew(C, ctorArgs):
  Tobj = newtemp(ref(C))
  emit( Tobj = newobj C, size(C) )
  emit( param Tobj )
  for a in ctorArgs:
    A = visit(a); emit( param A.place ); freeIfTemp(A)
  if hasCtor(C):
    emit( call f_<C>_constructor, len(ctorArgs)+1 )
  return Tobj
```

## 11. Ejemplos integrados

**Acceso encadenado y actualización:**

```bash
t1 = p.x
t2 = q.y
t3 = t1 + t2
p.x = t3
```

**Métodos set/get:**

```bash
param b
param 10
call f_Box_set, 2

param b
t1 = call f_Box_get, 1
z  = t1
```

**Herencia con override (estático):**

```bash
t2 = newobj B, 4
param t2
param 4
call f_A_constructor, 2
b = t2

param b
t4 = call f_B_get, 1
r2 = t4
```
