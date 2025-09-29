# ⚙️ Preparación del Entorno para Lab 1 (ANTLR + Python)

Este documento describe los pasos necesarios para preparar el entorno de trabajo para el **Laboratorio 1**, asumiendo que ANTLR ya está instalado y configurado globalmente en tu sistema (incluyendo alias `antlr4` y `grun`).

## ✅ Paso 1: Ubicarse en el directorio del proyecto

Navega al directorio objetivo para probar el entorno de ANTLR:

```bash
cd ~/ruta-program/
```

## ✅ Paso 2: Crear y activar entorno virtual de Python

Se recomienda usar un entorno virtual para mantener las dependencias organizadas y evitar conflictos con otros proyectos.

```bash
python3 -m venv venv
source venv/bin/activate
```

## ✅ Paso 3: Instalar ANTLR Runtime para Python

Dentro del entorno virtual, instala la librería necesaria para ejecutar el código generado por ANTLR:

```bash
pip install antlr4-python3-runtime
```
