"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MyCustomErrorListener = void 0;
const vscode_1 = require("vscode");
class MyCustomErrorListener {
    constructor(diagnostics, document) {
        this.diagnostics = diagnostics;
        this.document = document;
    }
    syntaxError(recognizer, offendingSymbol, line, charPositionInLine, msg, e) {
        // VS Code is 0-based lines, ANTLR is 1-based
        const lineIndex = line - 1;
        const range = new vscode_1.Range(lineIndex, charPositionInLine, lineIndex, charPositionInLine + 1);
        this.diagnostics.push({
            severity: vscode_1.DiagnosticSeverity.Error,
            message: msg,
            range,
            source: 'compiscript'
        });
    }
}
exports.MyCustomErrorListener = MyCustomErrorListener;
//# sourceMappingURL=ErrorListener.js.map