# Workflow Proyecto

## OBJETIVO GENERAL

Diseñar e implementar la **fase semántica** y la **generación de código intermedio** para Compiscript, utilizando los principios de la **Traducción Dirigida por la Sintaxis (DDS)**. Esto implica enriquecer el árbol de análisis sintáctico con información semántica relevante, validar reglas del lenguaje y preparar estructuras que luego permitirán generar el código de salida del programa.

## FLUJO LÓGICO EXPLICADO

### 0. **Preparación base del entorno**

Antes de comenzar con semántica, se debe tener listo el parser que genera el árbol de análisis sintáctico (AST) del programa. Este árbol será el insumo principal para toda la verificación semántica y para la traducción posterior.

Esto implica:

* Haber ejecutado la generación del lexer y parser.
* Tener un archivo de entrada que represente un programa en Compiscript.
* Validar que el árbol se construye correctamente, aunque aún no tenga análisis semántico.

**Ejemplo:** Si el programa dice `let x = 5 + 3;`, el parser debe construir un árbol que muestre esta declaración con una operación de suma como expresión.

### 1. **Recorrido del AST: diseño del Visitor**

Para aplicar reglas semánticas, necesitamos recorrer el AST y ejecutar acciones específicas según el tipo de nodo. Esto se realiza mediante un diseño conocido como *Visitor*, que permite asociar funciones semánticas a cada tipo de producción gramatical.

**¿Por qué es clave este paso?**
Porque sin recorrer el árbol no se puede propagar información (como tipos o nombres) ni verificar errores. Es como hacer un tour por el programa para ver qué está bien y qué está mal.

**Ejemplo:** Al recorrer un nodo que representa `x = y + 2`, el Visitor debe determinar:

* si `x` está declarado,
* si `y` también lo está,
* si ambos tienen tipos compatibles con la operación de suma.

### 2. **Diseño de la tabla de símbolos y entornos**

La tabla de símbolos es donde se guarda la información que el compilador necesita sobre cada identificador (variables, constantes, funciones, clases, etc.). Es la memoria del compilador durante la fase de análisis.

También se necesita una estructura para manejar los **ámbitos** o **scopes**. Por ejemplo, una variable puede estar declarada dentro de una función y no ser visible afuera. Para eso, se utilizan mecanismos como pilas de entornos.

**¿Por qué ahora y no después?**
Porque cada vez que visites una declaración en el árbol, debes registrar información en la tabla. Si no la tienes lista, no puedes avanzar.

**Ejemplo:**

* Al encontrar `let a: integer = 10;`, se guarda que `a` es un entero, variable, y su posición en la memoria.
* Si más adelante se hace `a = true;`, se podrá consultar la tabla y detectar un error de tipo.

### 3. **Definición del sistema de tipos y sus propiedades**

Para validar que las operaciones tienen sentido, hay que establecer qué tipos existen en el lenguaje, cuál es su tamaño (para futuras fases de memoria o código) y qué operaciones son válidas entre ellos.

**¿Por qué aquí?**
Porque esta información será usada en:

* verificaciones de expresiones (`a + b`)
* asignaciones (`x = expr`)
* llamadas a funciones (`f(3, true)`)

**Ejemplo:**

* Si `int` ocupa 4 bytes y `bool` ocupa 1, ya sabes cuánto desplazar la memoria al declarar variables.
* También sabes que `int + int` es válido, pero `int + bool` debe marcar error, salvo que exista un casteo implícito.

### 4. **Verificaciones semánticas simples (casos mínimos)**

Se comienza validando aspectos básicos: que las variables estén declaradas antes de usarse, que las constantes se inicialicen correctamente, y que no haya duplicidad de nombres en un mismo ámbito.

Esto permite:

* probar la tabla de símbolos,
* asegurar que el Visitor está conectado correctamente,
* comenzar a registrar errores.

**Ejemplo:**

* Detectar que `let a: integer; a = 5;` es válido.
* Detectar que `a = 5;` sin declaración previa es un error.
* Detectar que `const PI;` sin asignación es inválido.

### 5. **Aplicar Traducción Dirigida por la Sintaxis (DDS)**

Aquí se utilizan los conceptos de atributos **sintetizados** para propagar información hacia arriba en el árbol. Por ejemplo, cuando se visita una expresión `a + b`, se evalúan los tipos de `a` y `b` y se propaga el tipo resultante hacia su nodo padre.

**¿Por qué ahora?**
Porque ya tienes recorrido y tabla, ahora puedes agregar lógica de evaluación a cada nodo.

**Ejemplo extendido:**
Supón que estás evaluando `a + b`:

* `a` es `integer`, `b` es `integer`, entonces el resultado también es `integer`.
* Si `a` es `integer` y `b` es `boolean`, generas un error semántico o aplicas un casteo si está permitido.

Esto es precisamente lo que significa aplicar DDS: propagar valores semánticos según reglas asociadas a la gramática.

### 6. **Manejo de trazas y mensajes de error (logs)**

Al validar semántica, se producen errores: variables no declaradas, tipos incompatibles, etc. Para depurarlos y reportarlos, conviene tener un sistema de registro de errores.

**¿Por qué ahora?**
Porque ya estás validando reglas. Si no guardas los errores detectados, será difícil rastrear fallos o mostrar los mensajes al usuario del IDE.

**Ejemplo:**

* Si en un programa aparece `let a: string = 5;`, puedes registrar el error en un archivo y permitir que el IDE lo lea.
* También podrías registrar advertencias o tiempos de análisis para medir rendimiento.

### 7. **Diseño de la estructura del código intermedio**

El código intermedio es una representación más abstracta que el ensamblador, pero más cercana a la máquina que el código fuente. Por ejemplo, en lugar de `x = a + b`, se genera algo como:

```bash
t1 = a + b
x = t1
```

Esto permite separar semántica de código máquina. El código intermedio se construye también usando DDS: al visitar un nodo, se generan instrucciones y se guardan temporalmente.

**¿Por qué después de DDS?**
Porque el resultado de evaluar atributos (como tipo, valor, o estructura de la expresión) es lo que permite generar instrucciones correctas.

**Ejemplo:**
Si visitas un nodo de multiplicación `x * y`, y sabes que ambos son enteros, puedes generar una instrucción como `t2 = x * y`, donde `t2` es una variable temporal que luego se usa en otra operación.

### 8. **Enlace de todo el análisis con el driver**

Finalmente, conectas el visitante, la tabla de símbolos, el registro de errores y el generador de código intermedio con el punto de entrada del programa. Esto permite ejecutar todo el análisis semántico al compilar cualquier archivo fuente.

**¿Por qué hasta el final?**
Porque ahora ya tienes todas las piezas, y lo que necesitas es ejecutarlas en orden, asegurando que el árbol se recorra, que los errores se registren, y que el resultado se conserve o imprima.

**Ejemplo:**
Al correr `program.cps`, se analiza todo el código, se generan instrucciones intermedias, se detectan errores, y se dejan los resultados en archivos accesibles al IDE.

## RESUMEN DE ETAPAS

| Etapa | Acción                                 | Propósito                              |
| ----- | -------------------------------------- | -------------------------------------- |
| 0     | Tener el AST listo                     | Punto de partida                       |
| 1     | Diseñar un Visitor                     | Poder recorrer y operar sobre el árbol |
| 2     | Crear tabla de símbolos y entornos     | Controlar declaraciones y ámbitos      |
| 3     | Definir tipos y tamaños                | Base para validaciones y memoria       |
| 4     | Validar reglas básicas                 | Confirmar estructura y flujo           |
| 5     | Aplicar DDS con atributos sintetizados | Propagar semántica por el árbol        |
| 6     | Registrar errores y trazas             | Trazabilidad y debugging               |
| 7     | Empezar a construir código intermedio  | Salida útil para fases siguientes      |
| 8     | Integrar todo en el driver             | Permitir compilación automática        |
