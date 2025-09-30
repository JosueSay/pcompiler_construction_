# Guía práctica del lenguaje Compiscript

## 1. Programa mínimo

```c
// Variables globales, funciones y clases pueden declararse a nivel superior

let x: integer = 1;

function main(): void {
  // punto de entrada (opcional según tus pruebas)
}
```

## 2. Variables y constantes

### 2.1 `let` (variable mutable)

```c
let a: integer = 10;
a = a + 1;        // ok
```

### 2.2 `const` (constante, inicialización obligatoria)

```c
const K: integer = 10;  // obligatorio inicializar
K = 1;                  // ❌ error: no se puede modificar una constante
```

**Reglas semánticas:**

* La **asignación** debe respetar tipos: el valor del lado derecho debe ser **asignable** al tipo declarado.
* **Inicialización** de `const` es obligatoria en su declaración.
* No se permite **redeclarar** un mismo nombre en el **mismo scope** (ver §9).

**Errores típicos:**

* “Asignación incompatible: no se puede asignar `<from>` a `<to>`”
* “No se puede modificar la constante ‘K’”
* “Identificador redeclarado en el mismo ámbito”

## 3. Tipos y expresiones

### 3.1 Tipos escalares

* `integer`, `boolean`, `string` (usado en tests de error), y referencias a arreglos/clases.

### 3.2 Aritmética

```c
let z: integer = (a + b) * (c - 1);
let n: integer = -z;         // unario
```

> Operadores `+ - * /` requieren operandos numéricos (p. ej., `integer`).

### 3.3 Lógicas y comparaciones

```c
let p: boolean = (x < 10) || (x > 20) && (x != y);
let q: boolean = !(x == 0);
```

> `&&`, `||`, `!` trabajan con `boolean`.
> Comparaciones devuelven `boolean` y requieren **operandos compatibles**.

**Errores típicos:**

* “`&&`/`||` requiere operandos boolean”
* “Comparación con operandos incompatibles”
* “La condición debe ser `boolean`” (en estructuras de control)

## 4. Arreglos (listas)

### 4.1 Literales y homogeneidad

```c
let xs: integer[] = [1, 2, 3];        // ok
let m: integer[][] = [[1,2],[3,4]];   // ok
```

> Los literales deben ser **homogéneos**: todos los elementos con el mismo tipo base.

### 4.2 Indexación y asignación indexada

```c
let a: integer[] = [10,20,30];
let i: integer = 1;

let v: integer = a[i];    // lectura
a[i] = v + 5;             // escritura
```

**Reglas semánticas:**

* El **índice** debe ser `integer`.
* En `a[i] = expr`, el tipo de `expr` debe ser **asignable** al **tipo de elemento** de `a`.

**Errores típicos:**

* “Índice no entero en acceso/asig. de arreglo”
* “Asignación incompatible en arreglo: no se puede asignar `<from>` a `<to>`”
* “Asignación indexada sobre un no-arreglo”
* “Asignación indexada a propiedad en no-objeto” (p. ej., `y.data[0]` cuando `y` no es objeto con campo `data`)

> **Nota sobre ejecución**: El *bounds checking* (índice fuera de rango) se maneja en la etapa de TAC/runtime; la semántica se enfoca en tipos.

## 5. Lvalues: variables, campos y elementos

```c
x = 1;             // variable
p.x = p.x + 1;     // campo de objeto
a[i] = 99;         // elemento de arreglo
```

**Reglas:**

* El lado izquierdo debe ser un **l-value** válido: identificador, `obj.campo`, `arr[idx]`.
* El tipo del lado derecho debe ser **asignable**.

## 6. Control de flujo

### 6.1 `if` / `if-else`

```c
if (x < 3 || (y > 7 && x != y)) {
  x = 0;
} else {
  x = 1;
}
```

> La **condición** debe ser `boolean`.

### 6.2 `while`, `do-while`, `for`

```c
while (i < n) { i = i + 1; }

do { a = a + 2; } while (a < 5);

for (k = 0; k < 3; k = k + 1) { s = s + k; }
```

**Reglas:**

* Condiciones deben ser `boolean`.
* `continue`/`break` **solo dentro** de bucles:

  * `continue` salta a la **actualización** en `for` o a la **re-evaluación** de condición en `while`/`do-while`.
  * `break` sale del bucle actual.

### 6.3 `switch` con *fall-through*

```c
switch (op) {
  case 0: r = 10; break;
  case 1: r = 20;         // sin break → cae a default
  default: r = r + 1;
}
```

**Errores típicos:**

* “`break`/`continue` fuera de bucle”
* “Condición no booleana en `if`/`while`/`for`/`do-while`”

## 7. Funciones y procedimientos

### 7.1 Declaración y llamada

```c
function add(a: integer, b: integer): integer { return a + b; }

let u: integer = 4;
let v: integer = 7;
let r: integer = add(u + 1, v);
```

**Reglas:**

* Chequeo de **número** y **tipo** de argumentos por posición.
* El **tipo de retorno** debe coincidir con la declaración.
* `return expr;` **obligatorio** en todos los caminos para funciones **no-void**.
* `return;` **solo** en funciones `void`.

### 7.2 Recursión

```c
function fact(n: integer): integer {
  if (n <= 1) { return 1; }
  return n * fact(n - 1);
}
```

### 7.3 Funciones anidadas / closures

```c
function mk(): integer {
  let base: integer = 10;
  function add(n: integer): integer { return base + n; }  // captura 'base'
  return add(5);
}
```

**Errores típicos:**

* “`return` fuera de función”
* “Falta `return` en camino de ejecución de función no-void”
* “Tipo devuelto no asignable al tipo de retorno”

## 8. Clases y objetos

### 8.1 Definición con campos y métodos

```c
class Counter {
  var x: integer;
  function constructor(init: integer): void { this.x = init; }
  function inc(): void { this.x = this.x + 1; }
  function get(): integer { return this.x; }
}

let c: Counter = new Counter(5);
c.inc();
let g: integer = c.get();
```

**Reglas:**

* `this` **solo** en el cuerpo de métodos/constructor.
* Acceso a **campos existentes** y **métodos declarados**:

  * `obj.f` válida si `f` pertenece al tipo de `obj`.
* Llamadas a **constructor** coherentes con su firma.

### 8.2 Campos `let` / `var` / `const`

```c
class Box {
  let v: integer;
  function constructor(v: integer) { this.v = v; }
}
```

> `const K` dentro de clase: constante de clase (inmutable).

### 8.3 Herencia (básica con override)

```c
class A {
  let x: integer;
  function constructor(x: integer) { this.x = x; }
  function get(): integer { return this.x; }
}
class B : A {
  function get(): integer { return this.x + 1; } // override
}
```

**Errores típicos:**

* “Uso de `this` fuera de una clase”
* “Campo/método inexistente en el tipo”
* “Llamada a constructor incompatible”

## 9. Ámbitos (*scopes*) y tabla de símbolos

### 9.1 Creación/cierre de ámbitos

* Se crea un **nuevo ámbito** en:

  * Cuerpo de función/método/constructor,
  * Cuerpo de clase,
  * Bloques `{ ... }`,
  * Cuerpos de `if`/`else`/bucles/switch.
* Al cerrar el ámbito se descartan sus símbolos.

### 9.2 Resolución de nombres y *shadowing*

```c
let a: integer = 1;
{
  let a: integer = 2; // sombra del 'a' externo
  let x: integer = a; // usa el interno (2)
}
let y: integer = a;   // usa el externo (1)
```

**Políticas:**

* **Redeclaración prohibida** en el **mismo** ámbito.
* *Shadowing* permitido en ámbitos **internos** (son símbolos distintos).
* **Uso antes de declarar** → error.

**Errores típicos:**

* “Identificador redeclarado en el mismo ámbito”
* “Variable no declarada”

## 10. Guía de errores frecuentes

| Mensaje (o similar)                                                   | ¿Qué significa?                                       | Ejemplo que lo dispara                   |
| --------------------------------------------------------------------- | ----------------------------------------------------- | ---------------------------------------- |
| **Índice no entero en asig./acceso de arreglo: se encontró `<tipo>`** | El índice no es `integer`.                            | `a[true] = 1;`                           |
| **Asignación incompatible: no se puede asignar `<from>` a `<to>`**    | Tipos incompatibles en asignación.                    | `a[i] = "hi";` cuando `a: integer[]`     |
| **Asig. indexada sobre un no-arreglo**                                | Estás usando `[]` sobre algo que no es arreglo.       | `c.x[0] = 1;` con `x: integer`           |
| **Asig. indexada a propiedad en no-objeto: 'integer'**                | Accediste `algo.campo[...]` pero `algo` no es objeto. | `y.data[0] = 1;` con `y: integer`        |
| **No se puede modificar la constante ‘a’**                            | Intentaste asignar a un `const`.                      | `const a = [1]; a[0] = 2;`               |
| **Uso de `this` fuera de una clase**                                  | `this` sólo existe en métodos/constructor.            | En una función global                    |
| **Código inalcanzable / DeadCode**                                    | Hay sentencias tras `return` (o flujo terminado).     | `return; this.x = 1;`                    |
| **`break`/`continue` fuera de bucle**                                 | Solo válidos dentro de `while`/`for`/`do`             | En una función sin bucle                 |
| **Condición debe ser `boolean`**                                      | La guardia de `if`/`while`/… no es booleana.          | `if (3) { ... }`                         |
| **`return` fuera de función**                                         | Aparece `return` en nivel global/bloque externo.      | Nivel superior                           |
| **Falta `return` en función no-void**                                 | Algún camino no devuelve valor.                       | `function f(): int { if (p) return 1; }` |
| **Variable no declarada**                                             | Nombre sin símbolo visible en el scope actual.        | `x = 1;` sin `let x`                     |

> Los mensajes exactos pueden variar levemente según `diagnostics.py`, pero la semántica subyacente coincide con lo descrito.

## 11. Patrón de trabajo recomendado

1. **Declara y tipa** tus variables/funciones/clases.
2. **Compón** expresiones respetando tipos (numéricos para aritmética, booleanos para lógica).
3. **Usa arreglos** homogéneos, con índices `integer`.
4. **Estructura el control** con condiciones booleanas y respeta el contexto de `break`/`continue`/`return`.
5. **En clases**, inicializa en constructor y usa `this` dentro de métodos.
6. **Piensa en scopes**: declara nombres en el ámbito donde se usan; evita redeclarar en el mismo nivel.

## 12. Mini-recetario (copiar/pegar)

### 12.1 Sumar sólo impares de 0..N

```c
function sumOdds(n: integer): integer {
  let s: integer = 0;
  let i: integer = 0;
  while (i < n) {
    i = i + 1;
    if (i % 2 == 0) { continue; }
    s = s + i;
  }
  return s;
}
```

### 12.2 Clase con campo lista

```c
class Box {
  var data: integer[];
  function constructor(): void { this.data = [7,8,9]; }
  function get(i: integer): integer { return this.data[i]; }
  function put(i: integer, v: integer): void { this.data[i] = v; }
}
```

### 12.3 Factorial recursivo

```c
function fact(n: integer): integer {
  if (n <= 1) { return 1; }
  return n * fact(n - 1);
}
```
