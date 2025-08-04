# Compis Script 🧠

## 🛠️ Entorno de desarrollo

A continuación se detallan las versiones actuales de las herramientas utilizadas en el proyecto. Tener en cuenta que estas pueden cambiar en el futuro si surge algún problema de compatibilidad con dependencias.

* **ANTLR Parser Generator**: v4.13.1  
* **Python**: 3.10.12  
* **pip**: 25.2  
* **Docker**: 28.3.0 (build 38b7060)  
* **WSL2 (Windows Subsystem for Linux)**: v22.4.5 (o superior)  

## 🚀 Ejecución del archivo

Desde la raíz del repositorio puedes ejecutar el siguiente comando para configurar el entorno de desarrollo:

```bash
./setup.sh
```

Este script crea el entorno virtual de Python e instala las dependencias necesarias.

Una vez finalizado, puedes generar el código Python para el *lexer* y *parser* a partir de la gramática ANTLR con:

```bash
./generate_code_py.sh
```

Este comando utiliza la gramática `Compiscript.g4` y genera los archivos necesarios dentro del directorio `antlr_gen/`.
