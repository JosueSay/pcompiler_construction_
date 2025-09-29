# 🧩 Módulo `antlr_gen`

Contiene **solo código generado por ANTLR 4.13.1** a partir de `Compiscript.g4`. La idea es **separar** artefactos generados del código fuente del repositorio.

## 📦 Qué hay aquí

- `CompiscriptLexer.py`, `CompiscriptParser.py` → léxico y parser generados. :contentReference[oaicite:0]{index=0} :contentReference[oaicite:1]{index=1}  
- `CompiscriptListener.py`, `CompiscriptVisitor.py` → listener/visitor base. :contentReference[oaicite:2]{index=2} :contentReference[oaicite:3]{index=3}  
- Archivos auxiliares: `*.tokens`, `*.interp` (tablas/ATN del lexer/parser).  

> Todos indican en el encabezado que fueron **generados por ANTLR 4.13.1**.

## 🔄 Regenerar

Desde la raíz del repo:

```bash
./scripts/generate_code_py.sh
```

Genera/actualiza los archivos en `antlr_gen/` usando la gramática `src/utils/Compiscript.g4`.

## 🚫 No editar a mano

Estos archivos se **sobrescriben** al regenerar. Si notas residuos antiguos, puedes limpiar la carpeta y volver a generar.

## 🐍 Uso (importación)

Ejemplo mínimo en Python:

```python
from antlr4 import InputStream, CommonTokenStream
from antlr_gen.CompiscriptLexer import CompiscriptLexer
from antlr_gen.CompiscriptParser import CompiscriptParser

stream = InputStream("let x: integer = 1;")
lexer = CompiscriptLexer(stream)
tokens = CommonTokenStream(lexer)
parser = CompiscriptParser(tokens)
tree = parser.program()
```
