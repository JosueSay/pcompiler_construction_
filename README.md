# Compis Script 🧠

## 🛠️ Entorno de desarrollo

Este proyecto utiliza las siguientes herramientas. Ten en cuenta que las versiones pueden cambiar en el futuro por motivos de compatibilidad:

- **ANTLR Parser Generator**: v4.13.1  
- **Python**: 3.10.12  
- **pip**: 25.2  
- **Docker**: 28.3.0 (build 38b7060)  
- **WSL2 (Windows Subsystem for Linux)**: v22.4.5 (o superior)  

## 🚀 Configuración y ejecución

Desde la raíz del repositorio, ejecuta el siguiente comando para configurar el entorno de desarrollo:

```bash
./setup.sh
```

Este script crea un entorno virtual de Python e instala todas las dependencias necesarias.

### Generar código con ANTLR

Una vez configurado el entorno, puedes generar el código en Python para el *lexer* y *parser* a partir de la gramática ANTLR:

```bash
./generate_code_py.sh
```

Este comando usa la gramática `Compiscript.g4` y genera los archivos dentro del directorio `antlr_gen/`.

## ▶️ Ejecución de pruebas

Para ejecutar un programa de prueba, coloca los archivos en la carpeta `src/test/...` y utiliza el comando:

```bash
CPS_VERBOSE=0 ./scripts/run.sh src/test/functions/all_in_one.cps 
```

### Parámetro `CPS_VERBOSE`

- **0** -> No genera logs del procedimiento semántico.
- **1** -> Genera un log detallado en la carpeta `src/logs/out`.

## 📂 Archivos generados en `src/logs/out`

Al ejecutar con logs habilitados, se generan los siguientes archivos:

- **`*ast.html`** -> Visualización en HTML del árbol sintáctico (AST).
- **`*symbols.html`** -> Tabla de símbolos en HTML.
- **`*semantic.log`** -> Registro detallado del proceso semántico.
- **`*symbols.log`** -> Tabla de símbolos en texto plano.
- **`*ast.txt`** -> Representación del AST en texto (base para el HTML).

## 🌐 Visualización en navegador

Para visualizar los resultados:

1. Instala la extensión **Live Server** en VS Code.

   ![Live Server](./images/liveserver.png)

2. Haz clic en el botón **"Go Live"** (parte inferior derecha de VS Code).

   ![Go Live](./images/GoLive.png)

3. Abre en tu navegador la dirección:

   ```bash
   Visitar http://172.20.112.1:5500/src/logs/out/ para abrir los archivos correspondientes
   ```

4. Selecciona el archivo HTML que quieras visualizar.

## 🎨 Extensión para Compis Script en VS Code

Para habilitar **resaltado de sintaxis** de Compis Script en VS Code:

1. Copia la extensión al directorio de VS Code:

   ```bash
   cd ide/
   cp -r cps ~\.vscode\extensions\
   ```

2. Cierra y vuelve a abrir VS Code.
