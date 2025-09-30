# Listado de todo lo que debe implementarse en la fase de análisis semántico de Compiscript

## 1. Verificación de tipos

1. Verificar tipos válidos en operaciones aritméticas (`+`, `-`, `*`, `/`) entre `integer` o `float`.
2. Verificar tipos válidos en operaciones lógicas (`&&`, `||`, `!`) entre `boolean`.
3. Verificar tipos compatibles en comparaciones (`==`, `!=`, `<`, `>`, `<=`, `>=`).
4. Verificar que en asignaciones el tipo del valor coincida con el tipo de la variable.
5. Validar inicialización obligatoria de constantes (`const`).
6. Validar el tipo de retorno de funciones.
7. Validar que las condiciones en estructuras de control (`if`, `while`, `for`, `switch`) sean de tipo `boolean`.
8. Detectar y reportar operaciones inválidas como aplicar operadores aritméticos a funciones o tipos no compatibles.

## 2. Validaciones estructurales y de control

9. Verificar que `break` y `continue` solo se usen dentro de bucles.
10. Verificar que `return` esté dentro del cuerpo de una función.
11. Verificar que el valor de retorno coincida con el tipo declarado de la función.
12. Detectar código muerto: instrucciones después de `return`, `break`, `continue`.

## 3. Manejo de funciones y procedimientos

13. Verificar que el número y tipo de argumentos en llamadas coincidan con la definición de la función.
14. Soportar funciones recursivas.
15. Soportar funciones anidadas y closures, incluyendo captura de variables del entorno.
16. Verificar que no haya múltiples funciones con el mismo nombre si no se permite sobrecarga.

## 4. Manejo de clases y objetos

17. Verificar acceso a atributos y métodos definidos en clases.
18. Verificar llamada correcta al constructor.
19. Verificar uso correcto de `this` dentro de clases.

## 5. Manejo de listas y estructuras de datos

20. Validar el tipo homogéneo en listas.
21. Validar que los índices de acceso sean de tipo `integer`.
22. Validar que se accedan solo atributos existentes en estructuras.

## 6. Manejo de ámbito y tabla de símbolos

23. Construir una tabla de símbolos con:

    * Nombre
    * Tipo
    * Categoría (variable, función, constante, clase, parámetro)
    * Ámbito
    * Lista de parámetros (si aplica)
    * Tipo de retorno (si aplica)
24. Gestionar jerarquía de ámbitos (global, bloques, funciones, clases).
25. Detectar uso de identificadores no declarados.
26. Prohibir redeclaraciones dentro del mismo ámbito.
27. Permitir ocultamiento válido de nombres entre ámbitos anidados.

## 7. Árbol sintáctico y recorrido

28. Construir un árbol de análisis sintáctico anotado con los atributos semánticos.
29. Implementar el recorrido usando Visitor o Listener de ANTLR para evaluar reglas semánticas.

## 8. Pruebas automáticas

30. Escribir pruebas que validen casos correctos por cada regla semántica.
31. Escribir pruebas con errores para cada tipo de violación semántica.
32. Mantener una batería de pruebas completa que cubra todas las validaciones.

## 9. IDE y documentación

33. Desarrollar un IDE funcional que permita al usuario escribir código y compilarlo.
34. Documentar la arquitectura del compilador.
35. Documentar las instrucciones para ejecutar el compilador.
36. Preparar el repositorio de GitHub con historial de contribuciones individuales.

## Parte relacionada a generación de código intermedio que se puede adelantar en análisis semántico

### 1. Cálculo y propagación de atributos

1. Calcular y propagar el tipo (`type`) de cada nodo del AST.
2. Calcular el tamaño (`width`) de cada tipo (ej. `integer = 4`, `float = 8`).
3. Asociar y propagar identificadores temporales para cada subexpresión.
4. Anotar el AST con información útil para código intermedio:

   * Tipos
   * Valores literales
   * Dirección u offset
   * Temporales

### 2. Preparación para estructura de memoria

5. Calcular y asignar desplazamientos (`offsets`) a variables dentro de sus ámbitos.
6. Mantener registro de tamaños totales por bloque/función/clase.
7. Registrar el tipo completo (ej. `integer[]`, `class Animal`, `array(2, integer)`).

### 3. Representación intermedia de expresiones

8. Preparar expresiones complejas para recorrido postorden.
9. Identificar subexpresiones repetidas que puedan representarse como DAG.
10. Preparar datos para emitir instrucciones en código de tres direcciones:

    * Asignaciones
    * Saltos condicionales/incondicionales
    * Operaciones con temporales
    * Llamadas a funciones con `param` y `call`

### 4. Base para generación posterior

11. Registrar las instrucciones y expresiones en un formato interno que pueda traducirse a:

    * Cuádruples
    * Tríples
    * Código con etiquetas (labels)

Esto permite que al terminar el análisis semántico, el compilador esté listo para traducir el programa fuente a una representación intermedia optimizada.
