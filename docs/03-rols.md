# Separación de actividades

## **Rol 1: Lógica semántica (Visitor + validaciones de tipos/control)**

**Responsable de:**

* Implementar el `SemanticVisitor` (o `Listener`) con las reglas semánticas.
* Validaciones de:

  * Tipos (1–8)
  * Control de flujo (9–12)
  * Funciones y procedimientos (13–16)
  * Clases y objetos (17–19)
  * Listas y estructuras (20–22)
* Anotar el AST con tipos y referencias para debugging.

**Archivos clave:**

* `semantic/SemanticVisitor.py`
* `semantic/types.py`
* `utils/errors.py`

**Colaboración con Rol 2:** lectura/escritura de la tabla de símbolos.

## **Rol 2: Tabla de símbolos + manejo de ámbitos**

**Responsable de:**

* Implementar `symbol_table.py` con soporte para:

  * Entradas por tipo de símbolo (variable, función, clase, parámetro)
  * Jerarquía de entornos (funciones, bloques, clases)
  * Búsqueda ascendente, detección de colisiones
* Validaciones de:

  * Identificadores no declarados
  * Redeclaraciones
  * Resolución de `this`, atributos, herencia
* Asignación de nombres internos, si aplica.

**Archivos clave:**

* `semantic/symbol_table.py`
* `utils/context.py` (manejo de entornos)

**Colaboración con Rol 1:** acceso a símbolos para validación semántica.

## **Rol 3: Pruebas + IDE + documentación + estructura del proyecto**

**Responsable de:**

* Crear estructura base del compilador (`src/`, `tests/`, etc.).
* Implementar pruebas automáticas para cada regla:

  * Casos válidos e inválidos
  * Agrupados por tipo de validación
* Diseñar y conectar el **IDE mínimo funcional**:

  * Frontend simple (puede ser CLI o web con tkinter/Flask)
  * Botón para compilar archivo `.cps` y ver salida de errores
* Escribir:

  * Documentación de arquitectura y cómo correr el compilador
  * README detallado del repositorio
  * Scripts útiles (`build.sh`, `run.sh`, etc.)

**Archivos clave:**

* `tests/semantic/*`
* `ide/`
* `README.md`, `scripts/`

**Colaboración con Rol 1 y 2:** pruebas y visibilidad de errores.

## **¿Qué tareas no se hacen en esta entrega? (opcionales)**

* Todo lo de **representación intermedia**, como DAG, temporales, offsets, instrucciones TAC (esos se omiten en esta fase y se inician en la siguiente).
