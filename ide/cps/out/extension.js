"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = require("vscode");
function activate(context) {
    console.log('CPS extension activated');
    vscode.window.showInformationMessage('CPS language extension activated!');
}
function deactivate() { }
//# sourceMappingURL=extension.js.map