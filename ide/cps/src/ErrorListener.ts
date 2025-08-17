import { Diagnostic, DiagnosticSeverity, Range } from 'vscode';
import { ANTLRErrorListener, RecognitionException, Recognizer } from 'antlr4ts';

export class MyCustomErrorListener implements ANTLRErrorListener<any> {
  constructor(
    private diagnostics: Diagnostic[],
    private document: { lineAt: (line: number) => { range: Range } }
  ) {}

  syntaxError<T>(
    recognizer: Recognizer<T, any>,
    offendingSymbol: any,
    line: number,
    charPositionInLine: number,
    msg: string,
    e: RecognitionException | undefined
  ): void {
    // VS Code is 0-based lines, ANTLR is 1-based
    const lineIndex = line - 1;
    const range = new Range(
      lineIndex,
      charPositionInLine,
      lineIndex,
      charPositionInLine + 1
    );

    this.diagnostics.push({
      severity: DiagnosticSeverity.Error,
      message: msg,
      range,
      source: 'compiscript'
    });
  }
}
