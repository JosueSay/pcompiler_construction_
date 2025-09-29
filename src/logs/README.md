# 📂 Carpeta de Logs y Resultados

En esta sección se almacenan todos los archivos de **logging** relacionados con la ejecución de programas:  

- **Semántica**  
- **TAC (Three Address Code)**  
- (Próximamente) **Generación de código**  

Además, aquí está la lógica para mostrar en **HTML** la tabla de símbolos y el **AST (Árbol de Sintaxis Abstracta)**.

## 🗂️ Estructura general

```bash
.
├── logger_semantic.py                  # Logger de fase semántica
├── reporters.py                        # Lógica para generar reportes HTML (AST, tabla de símbolos, etc.)
├── out/                                # Carpeta principal de resultados
│   └── <timestamp>_<nombre_test>.cps/
│       ├── ast.txt                     # AST en formato texto plano
│       ├── ast.html                    # AST representado en HTML
│       ├── program.tac                 # TAC en texto plano
│       ├── program.tac.html            # TAC en HTML
│       ├── workflow.log                # Log completo del flujo (fase semántica y/o TAC)
│       ├── symbols.log                 # Tabla de símbolos en formato texto
│       └── symbols.html                # Tabla de símbolos en HTML

```

## ⏱️ Organización por ejecuciones

Cada vez que se ejecuta un programa de prueba (`.cps`), se genera una nueva carpeta en `out/` con la siguiente convención:

```bash
<timestamp>_<nombre_del_test>.cps/
```

Ejemplo:

```bash
20250929-114833_obb_negativo.cps/
```

Esto asegura que cada ejecución queda registrada de forma independiente.

## 📑 Archivos generados por ejecución

- **`ast.txt`** -> Representación textual del AST.  
- **`ast.html`** -> AST renderizado como página web.  
- **`program.tac`** -> Código intermedio TAC en texto plano.  
- **`program.tac.html`** -> Representación del TAC en HTML.  
- **`workflow.log`** -> Log de depuración con todo el proceso de análisis semántico y/o generación TAC.  
- **`symbols.log`** -> Versión en texto de la tabla de símbolos.  
- **`symbols.html`** -> Versión HTML de la tabla de símbolos.  
