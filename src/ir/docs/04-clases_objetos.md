# Generación de TAC para Clases y Objetos en Compiscript

Este documento describió el diseño de **generación de Código de Tres Direcciones (TAC, Three-Address Code)** para **clases y objetos** en Compiscript. Se explicó cómo se tradujeron el **acceso a atributos y métodos**, las **llamadas al constructor**, el uso de **`this`**, la **gestión de entornos y scopes** en métodos, y las **reglas de inicialización y asignación de campos**, incluyendo manejo de **temporales** y justificación de decisiones.

## 1. Convenciones generales

Se representó el IR en dos vistas:

- **3AC textual**: archivo `.tac` con instrucciones lineales y etiquetas (`Lk:`).
- **Cuádruplos**: tuplas `(op, arg1, arg2, res)` en memoria.

Se definió que el acceso a **campos** y **métodos** utilizara una abstracción estable en TAC:

- Campos: `x = obj.f` y `obj.f = v` como operaciones de **carga/almacenamiento** basadas en `field_offsets` provistos por `ClassHandler`.
- Métodos: llamadas con **`this` como primer parámetro implícito**, resolviendo la etiqueta de destino con información semántica de `method_registry` y el tipo estático del receptor.

Se modeló el **pool de temporales por función/método**, con reciclaje **por sentencia**. Los temporales de un método quedaron aislados de otros (véase `docs/README_TAC_GENERATION.md` y el documento de funciones).

**Justificación.** Esta abstracción permitió mantener el TAC independiente del layout físico de objetos y, a la vez, preservar suficiente información para un backend que materialice base+desplazamiento o un esquema de despacho dinámico si se necesitara.

## 2. Acceso a atributos y métodos

### 2.1 Atributos: `obj.f` y `obj.f = v`

Se tradujo el acceso a campos como operaciones de alto nivel en 3AC:

- **Lectura:**

  ```bash
  t1 = obj.f
  x  = t1
  ```

- **Escritura:**

  ```bash
  obj.f = v
  ```

**Reglas de emisión.**

1. `obj` se tradujo a un `place` (identificador, temporal o literal `null` validado previamente).
2. Para lectura, se creó un temporal `t` y se emitió `t = obj.f`; luego, si el resultado se asignó, se copió a su destino.
3. Para escritura, se emitió `obj.f = place(v)`.

**Justificación.** Se mantuvo el acceso abstracto en TAC y se delegó a la tabla de símbolos/clases (`field_offsets`) el cálculo del desplazamiento real. Esto permitió que el backend transforme `obj.f` en `[obj + offset(f)]` sin recodificar la fase de TAC.

### 2.2 Métodos: `obj.method(a1, ..., an)`

Se representó como una llamada de función con `this` implícito:

```bash
; evaluación de argumentos en orden
param obj               ; this implícito
param a1
...
param an
t = call f_Class_method, n+1   ; si hubiera valor de retorno
; o call f_Class_method, n+1   ; si no retorna valor
```

**Reglas de emisión.**

1. Se evaluó `obj` y los argumentos en **orden izquierda->derecha**, materializando cada uno en un `place`.
2. Se emitieron `param` para `this` y para cada argumento.
3. Se resolvió la **etiqueta objetivo** como `f_<Clase>_<método>` a partir de `method_registry` y del tipo estático del receptor.
4. Si el método retornó valor, se creó un temporal `t_ret` del tipo adecuado y se emitió `t_ret = call f_..., n+1`; en caso contrario, `call f_..., n+1`.

**Justificación.** Se adoptó **despacho estático** consistente con la información de tipos del análisis semántico. Cuando el tipo concreto del receptor fue conocido (p. ej., `let b: B = new B(); b.m();`), se "devirtualizó" a la etiqueta correspondiente. Este diseño mantuvo el IR simple; un backend o fase posterior podría introducir tablas de métodos si se necesitara despacho dinámico.

## 3. Llamadas al constructor e inicialización

Se tradujo `new C(args...)` como **reserva** seguida de **inicialización** por constructor:

```bash
t_obj = newobj C, <size(C)>    ; pseudo-op que devuelve referencia
param t_obj                     ; this para el constructor
param a1
...
param an
call f_C___ctor, n+1            ; si existiera constructor
```

**Reglas de emisión.**

1. `newobj C, size` produjo una referencia a instancia con espacio para todos los campos (`size` provino de la suma de `width` de campos según `ClassHandler` y `type_system`).
2. Si la clase definió constructor (`__ctor`), se llamó con `this = t_obj` y los argumentos. Si no, se inicializó por defecto:

   - Referencias a `null`.
   - Tipos numéricos o booleanos según política de inicialización del proyecto (`src/semantic/analyzers/statements.py` y `type_system.py`).
3. El valor de la expresión `new` fue el temporal `t_obj`.

**Justificación.** Este patrón separó la **reserva** (semántica de heap abstracta en TAC) de la **inicialización** (constructor o defaults), alineando el flujo con el uso de `this` y con la semántica de argumentos validada en `classes.py` y `lvalues.py`.

### Ejemplo

Código:

```c
let p: Point = new Point(1, 2);
p.x = p.x + 3;
let d = p.dist();
```

3AC:

```bash
t0   = newobj Point, <size(Point)>
param t0
param 1
param 2
call f_Point___ctor, 3

t1 = p.x
t2 = t1 + 3
p.x = t2

param p          ; this
t3 = call f_Point_dist, 1
d  = t3
```

## 4. Uso de `this` dentro de métodos

Se modeló `this` como el **primer parámetro** del método y quedó disponible como identificador en el cuerpo:

```c
class Counter {
  x: int;
  inc(): void { this.x = this.x + 1; }
}
```

3AC del método:

```bash
f_Counter_inc:
enter f_Counter_inc, <frame>
t1   = this.x
t2   = t1 + 1
this.x = t2
return
```

**Justificación.** Este enfoque hizo explícita la identidad del receptor en el RA, soportó acceso a campos mediante el mismo mecanismo abstracto (`this.f`) y mantuvo la simetría con las llamadas a métodos desde fuera de la clase (que pasan `this` como primer argumento).

## 5. Gestión de entornos y scopes de objetos

- **Alcance léxico.** Los métodos heredaron el **scope léxico** de su definición para nombres locales y parámetros; `this` se insertó en el scope del método como símbolo especial con tipo `ClassType(C)`.
- **Campos y offsets.** `ClassHandler` registró `field_offsets` al consolidar los atributos (y su herencia). Cada acceso `obj.f` consultó ese mapa para la traducción abstracta.
- **Herencia.** El registro de clases y el `method_registry` verificaron firmas y sobrescritura; el TAC resolvió la etiqueta objetivo en base al tipo estático conocido. Si se necesitara despacho dinámico en escenarios de polimorfismo con tipos base, la fase posterior podría expandir a `vcall` con tablas de métodos; el TAC no quedó acoplado a dicha decisión.

**Justificación.** Mantener la **abstracción** a nivel TAC evitó comprometer la representación interna; el backend tuvo la flexibilidad de materializar el layout de objetos (incluyendo herencia y posible vtable) sin modificar el IR emitido.

## 6. Traducción detallada de accesos y llamadas a TAC

### 6.1 Acceso a campo como valor y como l-valor

- **Lectura**: `x = obj.f`

  ```bash
  t = obj.f
  x = t
  ```

- **Escritura**: `obj.f = expr`

  ```bash
  v = visit(expr)
  obj.f = v
  ```

### 6.2 Llamada a método sin retorno

```bash
param obj
param a1
...
param an
call f_Class_method, n+1
```

### 6.3 Llamada a método con retorno

```bash
param obj
param a1
...
param an
tret = call f_Class_method, n+1
use tret
```

### 6.4 Construcción y constructor

```bash
tobj = newobj C, <size(C)>
param tobj
param a1
...
param an
call f_C___ctor, n+1
; valor de 'new C(...)' es tobj
```

## 7. Reglas de inicialización y asignación de campos

- **Inicialización por constructor.** Cuando `__ctor` existió, se delegó la inicialización de campos al propio cuerpo del constructor (que pudo incluir asignaciones como `this.f = ...`).
- **Inicialización por defecto.** En ausencia de constructor, la fase de TAC no asignó valores por sí misma; se respetó la política semántica de inicialización por defecto (p. ej., referencias a `null`). Si se requirió emitir asignación explícita para default, se generó:

  ```bash
  this.f = <default_value>
  ```

  en el bloque del constructor sintético.
- **Asignaciones posteriores.** Cualquier `obj.f = expr` se emitió como almacén abstracto, después de evaluar `expr` con temporales reciclables.

**Justificación.** Centralizar la inicialización en el constructor (explícito o sintético) mantuvo el orden de efectos predecible y coherente con el modelo de RA y con el análisis de flujo (`controlFlow.py`).

## 8. Manejo de temporales y pools

- Se usó un **pool de temporales por método**, inicializado al entrar en `f_Class_method` y descartado al salir.
- Se reciclaron temporales en **post-orden por sentencia**; los resultados intermedios de expresiones (`t1`, `t2`, ...) se liberaron en cuanto se emitió la operación del padre.
- En llamadas a métodos y constructores, los temporales de evaluación de argumentos se liberaron inmediatamente después de `param` salvo que se necesitaran aguas arriba.

**Justificación.** Este esquema minimizó la presión de temporales, evitó interferencia entre funciones/métodos y simplificó pruebas del IR.

## 9. Pseudocódigo de emisión

### 9.1 Campo: lectura y escritura

```text
function emitFieldLoad(objExpr, field):
    O = visit(objExpr)
    T = newtemp(typeOfField(O.type, field))
    emit( T = O.place.field )
    freeIfTemp(O)
    return T

function emitFieldStore(objExpr, field, valExpr):
    O = visit(objExpr)
    V = visit(valExpr)
    emit( O.place.field = V.place )
    freeIfTemp(O); freeIfTemp(V)
```

### 9.2 Llamada a método

```text
function emitMethodCall(objExpr, method, args, retTypeOpt):
    O = visit(objExpr)
    emit( param O.place )
    for a in args:
        A = visit(a)
        emit( param A.place )
        freeIfTemp(A)
    if retTypeOpt:
        T = newtemp(retTypeOpt)
        emit( T = call f_<Class>_<method>, len(args)+1 )
        freeIfTemp(O)
        return T
    else:
        emit( call f_<Class>_<method>, len(args)+1 )
        freeIfTemp(O)
        return None
```

### 9.3 Construcción

```text
function emitNew(Class, ctorArgs):
    Tobj = newtemp(ref(Class))
    emit( Tobj = newobj Class, size(Class) )
    emit( param Tobj )
    for a in ctorArgs:
        A = visit(a)
        emit( param A.place )
        freeIfTemp(A)
    if hasCtor(Class):
        emit( call f_<Class>___ctor, len(ctorArgs)+1 )
    else:
        ; opcional: inicialización por defecto mediante constructor sintético
    return Tobj
```

## 10. Ejemplos integrados

### 10.1 Acceso encadenado y actualización de campo

```c
p.x = p.x + q.y;
```

3AC:

```bash
t1 = p.x
t2 = q.y
t3 = t1 + t2
p.x = t3
```

### 10.2 Método con lectura/escritura de campos

```c
class Box { v: int; set(x: int): void { this.v = x; } get(): int { return this.v; } }
let b = new Box();
b.set(10);
let z = b.get();
```

3AC:

```bash
t0 = newobj Box, <size(Box)>
param t0
call f_Box___ctor, 1
b = t0

param b
param 10
call f_Box_set, 2

param b
t1 = call f_Box_get, 1
z  = t1
```

### 10.3 Herencia con override (despacho estático con tipo conocido)

```c
class A { m(): int { return 1; } }
class B : A { m(): int { return 2; } }
let x: B = new B();
let r = x.m();
```

3AC:

```bash
t0 = newobj B, <size(B)>
param t0
call f_B___ctor, 1
x = t0

param x
t1 = call f_B_m, 1
r  = t1
```

**Nota.** El despacho se resolvió estáticamente a `f_B_m` porque el tipo del receptor fue `B` en análisis semántico. De requerirse late-binding sobre un tipo base, una fase posterior podría reescribir a una forma `vcall`.
