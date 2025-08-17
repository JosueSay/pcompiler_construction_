"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
const vscode = require("vscode");
const antlr4ts_1 = require("antlr4ts");
const CompiscriptLexer_1 = require("./parser/CompiscriptLexer");
const CompiscriptParser_1 = require("./parser/CompiscriptParser");
const ErrorListener_1 = require("./ErrorListener");
function activate(context) {
    const diagnostics = vscode.languages.createDiagnosticCollection('cps');
    context.subscriptions.push(diagnostics);
    vscode.workspace.onDidChangeTextDocument(event => {
        if (event.document.languageId !== 'cps')
            return;
        const text = event.document.getText();
        // ANTLR setup
        const inputStream = antlr4ts_1.CharStreams.fromString(text);
        const lexer = new CompiscriptLexer_1.CompiscriptLexer(inputStream);
        const tokenStream = new antlr4ts_1.CommonTokenStream(lexer);
        const parser = new CompiscriptParser_1.CompiscriptParser(tokenStream);
        // Collect errors
        const errors = [];
        parser.removeErrorListeners();
        parser.addErrorListener(new ErrorListener_1.MyCustomErrorListener(errors, event.document));
        try {
            parser.program(); // entry rule in your grammar
        }
        catch (e) {
            // catch parser crashes (rare)
        }
        // Push diagnostics to VS Code
        diagnostics.set(event.document.uri, errors);
    });
}
//# sourceMappingURL=extension.js.map