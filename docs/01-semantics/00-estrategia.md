# Fase Semántica de Compiscript

Este documento describe el **modelo, reglas y convenciones** empleadas en la **fase semántica** del compilador de Compiscript. Cubre: sistema de tipos y asignabilidad, manejo de ámbitos y símbolos, funciones (parámetros/retorno/recursión/closures), control de flujo y verificaciones generales (constantes, duplicados, código muerto), alineado con la rúbrica del curso.

## 1. Arquitectura y responsabilidades

La fase semántica se implementa con visitantes sobre el AST, apoyándose en:

* **Sistema de tipos**: definición de tipos base y compuestos y sus reglas de asignabilidad/resultado de operaciones (ver §2). Tipos disponibles: `integer`, `float`, `boolean`, `string`, `class <C>`, `array<T>`, `void`, `null`, y tipo sentinela `error` para *no-cascada* de fallos.  
* **Resolución/validación de tipos**: utilidades para resolver anotaciones (incluyendo `[]`) y validar “tipos conocidos” (clases declaradas, prohibición de `void[]`).  
* **Diagnósticos**: acumulación de errores semánticos con línea/columna, evitando detener la compilación y registrando en logs.
* **Funciones**: declaración, chequeo de parámetros/retorno, *frame size* por alcance, *closures* (capturas) y contrato de retorno (incluye retorno implícito en `void`).  
* **Ámbitos/Símbolos**: alta de símbolos por categoría (`FUNCTION`, `PARAMETER`, etc.), offsets y cierre de *frame* al salir del alcance de la función. (Véase llamadas a `scopeManager.addSymbol/enterScope/closeFunctionScope` en el flujo de funciones.)  

> **Estándar de diseño**: separación estricta entre **comprobaciones semánticas** (antes de emitir IR) y **emisión posterior**; propagación de `ErrorType` para no-cascada y validación de “tipos conocidos”.  

## 2. Sistema de tipos y reglas

### 2.1 Tipos y tamaños

Se definen clases de tipo y un mapa de anchos para soporte de *frame size* y direccionamiento posterior. Strings, clases y arreglos se modelan como **referencias** (8 bytes).

### 2.2 Asignabilidad

Reglas de `isAssignable(target, value)`:

* Propaga `ErrorType` para evitar cascada de errores.
* `null` asignable a tipos **de referencia** (string, class, array).
* `Array<T1> ← Array<T2>` solo si `T1 ← T2` recursivo.
* `Class<A> ← Class<B>` solo si `A == B` (sin subtipado por herencia en esta fase).
* Primitivos: **coincidencia exacta**.

### 2.3 Resultados de operaciones

* Aritmética: numéricos con *promoción mínima* (`int op float → float`, `int op int → int`, `float op float → float`).
* Concatenación: `string + string → string` (solo `+`, no otros operadores con `string`).

### 2.4 Booleanos y lógicas

Las combinaciones lógicas usan validadores de tipo (en `expressions`) y reportan error si no son booleanos. (Ver uso de `resultLogical` y reporte de error en `visitLogicalAndExpr/OrExpr`.)

## 3. Resolución de tipos a partir de la gramática

* **Anotaciones** con `[]` para arreglos (p.ej. `integer[][]`): el resolutor calcula dimensión y enreda recursivamente `ArrayType`.  
* **Clases** en anotaciones: si el nombre base no es un primitivo reservado, se crea `ClassType(name)`. Validación posterior exige que la clase exista (*known classes*).  
* **Prohibido** `void[]`; se reporta diagnóstico.

## 4. Funciones y procedimientos

### 4.1 Declaración

* Se valida el **tipo de cada parámetro** (no puede ser `void`), y se registra el símbolo de la función con su `return_type`, `param_types` y `label` (para etapas posteriores).  
* Se crea un **nuevo scope** para el cuerpo y se insertan los **parámetros** como símbolos inicializados.

### 4.2 Retorno y terminación

* Se apila el **tipo de retorno esperado**; al finalizar el cuerpo:

  * Si la función es `void` y el bloque no terminó explícitamente, se **inyecta retorno implícito**.
  * Se cierra el scope de la función y se fija el **frame size** (para TAC).

### 4.3 Recursión y closures

* La función queda **auto-referenciable** por su símbolo (puede llamarse recursivamente).
* Se mantiene contexto de capturas (`captures`) y, si existen, se registra su *layout* en el símbolo de la función (base para closures).

> **Rúbrica**: verificación de número/tipo de argumentos, retorno correcto, recursividad y funciones anidadas/capturas: **soportado** por construcción del símbolo, pila de retorno y *captures*; los errores se reportan con contexto.  

## 5. Ámbitos, símbolos y reglas de visibilidad

* Cada **función** abre un scope nuevo; los **parámetros** y **locales** viven allí con offsets propios (base para RA). (Ver uso de `enterScope`/`addSymbol`/`closeFunctionScope`.)  
* **Redeclaración en el mismo ámbito**: se rechaza y se reporta error (mecanismo en `addSymbol`, evidenciado por *catch* y diagnóstico).
* **Shadowing** en ámbitos internos: permitido; cada símbolo tiene su propia ubicación lógica.
* **Tipos conocidos**: si una anotación refiere a clase no declarada, se reporta error (no se “adivina” el tipo).

## 6. Constantes, asignaciones y expresiones

* **Const**: inicialización obligatoria (la verificación está en los analizadores de declaraciones; si no hay valor o el tipo no coincide con el declarado, se reporta).
* **Asignaciones**: `isAssignable(target, value)` asegura compatibilidad; `null` solo a referencias; primitivos exactos; arrays comparan su **element type**.
* **Operaciones**:

  * Aritméticas: solo tipos numéricos; resultado por reglas de §2.3.
  * Booleanas: solo `boolean`; `&&`/`||`/`!` validan operandos y reportan error si no coinciden. (Ver `visitLogicalAndExpr/OrExpr` con `SemanticError` explícito.)

## 7. Estructuras de datos y listas

* Se modela `ArrayType(T)`; la semántica exige **homogeneidad** y **tipado de índices** (entero). La asignación entre arreglos respeta **compatibilidad por elemento** (`Array<T1> ← Array<T2>` si `T1 ← T2`).
* En accesos, el verificador semántico asegura que `a[i]` tenga `a: Array<U>` y `i: integer` (el *bounds-check* pertenece a TAC/runtime, documentado fuera de esta fase).

## 8. Clases, atributos y métodos

* **ClassType** soporta **miembros** y consulta con herencia (búsqueda en padre si no está en la clase).
* La semántica valida la **existencia** de atributos/métodos al usar `obj.f` / `obj.m(...)` y el tipo resultante de cada miembro. (La estructura de `ClassType.get_member/has_member` es la base del verificador.)
* **Constructores**: se valida el tipo de los parámetros del constructor cuando se usa `new C(...)` (la creación de objeto y RA de métodos/`this` se detalla en la documentación de TAC).

## 9. Control de flujo y reglas generales

* **Condiciones** en `if/while/do-while/for/switch`: deben ser de tipo `boolean`. Los analizadores de expresiones lógicas reportan errores tipando los operandos y devolviendo `ErrorType` ante usos inválidos.
* **`break`/`continue`**: validados por contexto de bucle (las pilas de contexto se gestionan en los analizadores de control de flujo; si se usa fuera de loop, se reporta).
* **`return`** solo dentro de funciones; verificación del **tipo de retorno** en línea con `expected_r`. La función `void` admite **retorno implícito** si el bloque no termina (ver §4.2).
* **Código muerto**: tras un `return` o terminación de flujo marcada por el analizador, los visitantes evitan seguir generando efectos (señalizado por *flags* de terminación que preservan coherencia del IR; visible en la restauración de `stmt_just_terminated`).

## 10. Manejo de errores y estrategia de “no-cascada”

* Cada error semántico se **registra** con línea y columna; se expone un API `Diagnostics.report/extend` y se loggea (no aborta de inmediato).
* Muchas comprobaciones devuelven `ErrorType` para **permitir continuar** y reportar más errores en una sola pasada. (Regla explícita en `isAssignable`: aceptar `ErrorType` como asignable para no-cascada.)

## 11. Qué permite la gramática + esta semántica

* **Tipos primitivos y compuestos** (arrays y clases) con **anidación de arreglos** (`T[][]...`) y validación de clases referenciadas.  
* **Funciones** con parámetros tipados, retorno opcional (`void`), **recursión** y funciones anidadas (base para **closures**).
* **Operadores** aritméticos y lógicos conforme a las **reglas del sistema de tipos** (incluida **concatenación** de strings solo con `+`).
* **Estructuras de control** (`if/while/do-while/for/switch`) que exigen **boolean** en la condición.
* **Clases** con miembros y herencia para *lookup*; el *dispatch* dinámico/estático es un tema de TAC/backend, manteniendo la semántica correcta de tipos de miembros.

## 12. Ejemplos de verificación típica

* **Parámetro inválido (void)**
  “Parámetro `p` no puede ser de tipo void” → se fuerza `ErrorType` y se continúa.
* **Clase desconocida** en anotación o arreglo → diagnóstico “Tipo de clase no declarado …”.
* **Asignación `null` a primitivo** → rechazada por `isAssignable` (solo referencias aceptan `null`).
* **Array\<T1\> ← Array\<T2\>** con `T1`≠`T2` → incompatible, salvo que `T1 ← T2` por misma regla recursiva.
* **Función `void` sin `return`** → retorno implícito inyectado al final.

## 13. Extensiones y decisiones deliberadas

* **No subtipado de clases** en asignación (solo `A==B`), simplifica verificación y evita *downcasts* implícitos; puede ampliarse más adelante.
* **Concatenación** restringida a `string + string` por claridad y para evitar reglas ambiguas entre números/strings.
* **No-cascada**: `ErrorType` “absorbe” verificaciones subsiguientes para producir más diagnósticos en una sola corrida.
