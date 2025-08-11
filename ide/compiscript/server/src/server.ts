import {
  createConnection,
  TextDocuments,
  ProposedFeatures,
  InitializeParams,
  SemanticTokensParams,
  SemanticTokens,
  SemanticTokensBuilder,
  TextDocumentSyncKind
} from 'vscode-languageserver/node';

import { TextDocument } from 'vscode-languageserver-textdocument';

import { CharStreams, CommonTokenStream } from 'antlr4ts';
import { CompiscriptLexer } from './antlr/CompiscriptLexer';
import { CompiscriptParser } from './antlr/CompiscriptParser';
import { ParseTreeWalker } from 'antlr4ts/tree';

// Create LSP connection
const connection = createConnection(ProposedFeatures.all);

// Track open documents
const documents: TextDocuments<TextDocument> = new TextDocuments(TextDocument);

connection.onInitialize((params: InitializeParams) => {
  return {
    capabilities: {
      textDocumentSync: TextDocumentSyncKind.Incremental,
      semanticTokensProvider: {
        legend: {
          tokenTypes: ['keyword', 'string', 'number', 'comment', 'variable', 'function', 'operator'],
          tokenModifiers: []
        },
        full: true
      }
    }
  };
});

// Map token types to LSP indexes
const tokenTypeMap: { [name: string]: number } = {
  'keyword': 0,
  'string': 1,
  'number': 2,
  'comment': 3,
  'variable': 4,
  'function': 5,
  'operator': 6
};

// Provide semantic tokens
connection.languages.semanticTokens.on((params: SemanticTokensParams): SemanticTokens => {
  const doc = documents.get(params.textDocument.uri);
  if (!doc) return { data: [] };

  const builder = new SemanticTokensBuilder();
  const inputStream = CharStreams.fromString(doc.getText());
  const lexer = new CompiscriptLexer(inputStream);
  const tokenStream = new CommonTokenStream(lexer);
  const parser = new CompiscriptParser(tokenStream);

  parser.removeErrorListeners(); // avoid console spam

  // For simplicity, walk tokens directly (can use a listener for richer data)
  tokenStream.fill();
  const tokens = tokenStream.getTokens();

  for (let token of tokens) {
    const tokenTypeName = getTokenTypeName(token.type, lexer);
    if (tokenTypeName && tokenTypeMap[tokenTypeName] !== undefined) {
      const start = doc.positionAt(token.startIndex);
      const length = token.text ? token.text.length : 0;
      builder.push(start.line, start.character, length, tokenTypeMap[tokenTypeName], 0);
    }
  }

  return builder.build();
});

// Helper: Map ANTLR token type to LSP semantic type
function getTokenTypeName(type: number, lexer: CompiscriptLexer): string | null {
  const tokenName = lexer.vocabulary.getSymbolicName(type);
  if (!tokenName) return null;

  if (tokenName.match(/STRING/)) return 'string';
  if (tokenName.match(/NUMBER/)) return 'number';
  if (tokenName.match(/COMMENT/)) return 'comment';
  if (tokenName.match(/(VAR|LET|CONST|IF|ELSE|WHILE|FOR|RETURN)/)) return 'keyword';
  if (tokenName.match(/IDENTIFIER/)) return 'variable';
  if (tokenName.match(/FUNC|FUNCTION/)) return 'function';
  if (tokenName.match(/PLUS|MINUS|STAR|SLASH|EQUAL|EQEQ/)) return 'operator';

  return null;
}

// Start listening
documents.listen(connection);
connection.listen();
