# ⚙️ Instalación de ANTLR en WSL con Python y Entorno Virtual

Este documento explica cómo instalar **ANTLR 4.13.1** en **WSL (Ubuntu)** con soporte para **Python**.

## ✅ Paso 1: Instalar dependencias necesarias

```bash
sudo apt update
sudo apt install -y openjdk-17-jdk python3 python3-pip curl
```

## ✅ Paso 2: Crear entorno virtual de Python

Ubícate en el directorio donde tengas el archivo `.g4` y el `Driver.py`. Por ejemplo:

```bash
cd ~/mis-proyectos/lab-1/program/
python3 -m venv venv
source venv/bin/activate
```

## ✅ Paso 3: Instalar runtime de ANTLR para Python

Dentro del entorno virtual activo, ejecuta:

```bash
pip install antlr4-python3-runtime
```

## ✅ Paso 4: Descargar el archivo JAR de ANTLR

```bash
mkdir -p ~/antlr
curl -o ~/antlr/antlr-4.13.1-complete.jar https://www.antlr.org/download/antlr-4.13.1-complete.jar
```

## ✅ Paso 5: Configurar ANTLR en el entorno de bash

Edita tu archivo `~/.bashrc`:

```bash
nano ~/.bashrc
```

Agrega al **final del archivo** estas líneas:

```bash
# ANTLR configuration
export CLASSPATH=".:$HOME/antlr/antlr-4.13.1-complete.jar:$CLASSPATH"
alias antlr4='java -jar $HOME/antlr/antlr-4.13.1-complete.jar'
alias grun='java org.antlr.v4.gui.TestRig'
```

Guarda y cierra el archivo (`Ctrl + O`, `Enter`, `Ctrl + X`).

## ✅ Paso 6: Recargar la configuración del shell

Para que los cambios surtan efecto:

```bash
source ~/.bashrc
```

## ✅ Paso 7: Verificar instalación de ANTLR

Ejecuta:

```bash
antlr4
```

Deberías ver un mensaje de ayuda con las opciones de ANTLR.

Con esto tienes listo ANTLR para usarlo con Python en WSL. A partir de aquí, puedes generar los archivos del parser con:

```bash
antlr4 -Dlanguage=Python3 MiniLang.g4
```
