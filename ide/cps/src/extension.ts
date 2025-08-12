import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  console.log('CPS extension activated');
  vscode.window.showInformationMessage('CPS language extension activated!');
}

export function deactivate() {}
