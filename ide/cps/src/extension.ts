import * as vscode from 'vscode';
import { CharStreams, CommonTokenStream } from 'antlr4ts';
import { CompiscriptLexer } from './parser/CompiscriptLexer';
import { CompiscriptParser } from './parser/CompiscriptParser';
import { MyCustomErrorListener } from './ErrorListener';

export function activate(context: vscode.ExtensionContext) {
  const diagnostics = vscode.languages.createDiagnosticCollection('cps');
  context.subscriptions.push(diagnostics);

  vscode.workspace.onDidChangeTextDocument(event => {
    if (event.document.languageId !== 'cps') return;

    const text = event.document.getText();

    // ANTLR setup
    const inputStream = CharStreams.fromString(text);
    const lexer = new CompiscriptLexer(inputStream);
    const tokenStream = new CommonTokenStream(lexer);
    const parser = new CompiscriptParser(tokenStream);

    // Collect errors
    const errors: vscode.Diagnostic[] = [];
    parser.removeErrorListeners();
    parser.addErrorListener(new MyCustomErrorListener(errors, event.document));

    try {
      parser.program(); // entry rule in your grammar
    } catch (e) {
      // catch parser crashes (rare)
    }

    // Push diagnostics to VS Code
    diagnostics.set(event.document.uri, errors);
  });
}
