# 🧠 Simulador MIPS con MARS

Este entorno permite ejecutar y probar programas en lenguaje ensamblador **MIPS** usando el simulador **MARS**.
Ideal para proyectos de compiladores o práctica de arquitectura de computadores.

## 📦 Requisitos

* **Java 21 o superior**
  Verifica la instalación:

  ```bash
  java --version
  ```

  Ejemplo de salida:

  ```bash
  openjdk 21.0.8 2025-07-15
  OpenJDK Runtime Environment (build 21.0.8+9-Ubuntu-0ubuntu122.04.1)
  OpenJDK 64-Bit Server VM (build 21.0.8+9-Ubuntu-0ubuntu122.04.1, mixed mode, sharing)
  ```

## ⚙️ Instalación de MARS

1. Descarga el simulador desde la página oficial:

   👉 [https://dpetersanderson.github.io/download.html](https://dpetersanderson.github.io/download.html)

   (Haz clic en el botón **"DOWNLOAD MARS"**)

2. Guarda el archivo descargado (`Mars4_5.jar`) en el directorio de tu proyecto.

## 🧩 Estructura mínima del proyecto

```bash
.
├── Mars4_5.jar
└── fibonacci.asm
```

## ▶️ Ejecución del simulador

### 1. Modo gráfico (interfaz MARS)

```bash
java -jar Mars4_5.jar
```

### 2. Modo consola (sin GUI)

```bash
java -jar Mars4_5.jar nc fibonacci.asm
```

El modo consola ejecuta directamente el programa y muestra la salida en terminal, por ejemplo:

```bash
The Fibonacci numbers are:
1 1 2 3 5 8 13 21 34 55 89 144
```

## 💡 Extensiones recomendadas para VS Code

1. **MIPS Support** – *por kdarkhan*

   > Proporciona resaltado de sintaxis y fragmentos de código MIPS.
   > 🟢 [Disponible en Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=kdarkhan.mips)

2. **MARScode** – *por Aanand Kainth*

   > Permite ejecutar programas MIPS directamente desde VS Code.
   > 🟢 [Disponible en Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=AanandKainth.marscode)
