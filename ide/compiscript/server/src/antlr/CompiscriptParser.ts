// Generated from Compiscript.g4 by ANTLR 4.9.0-SNAPSHOT


import { ATN } from "antlr4ts/atn/ATN";
import { ATNDeserializer } from "antlr4ts/atn/ATNDeserializer";
import { FailedPredicateException } from "antlr4ts/FailedPredicateException";
import { NotNull } from "antlr4ts/Decorators";
import { NoViableAltException } from "antlr4ts/NoViableAltException";
import { Override } from "antlr4ts/Decorators";
import { Parser } from "antlr4ts/Parser";
import { ParserRuleContext } from "antlr4ts/ParserRuleContext";
import { ParserATNSimulator } from "antlr4ts/atn/ParserATNSimulator";
import { ParseTreeListener } from "antlr4ts/tree/ParseTreeListener";
import { ParseTreeVisitor } from "antlr4ts/tree/ParseTreeVisitor";
import { RecognitionException } from "antlr4ts/RecognitionException";
import { RuleContext } from "antlr4ts/RuleContext";
//import { RuleVersion } from "antlr4ts/RuleVersion";
import { TerminalNode } from "antlr4ts/tree/TerminalNode";
import { Token } from "antlr4ts/Token";
import { TokenStream } from "antlr4ts/TokenStream";
import { Vocabulary } from "antlr4ts/Vocabulary";
import { VocabularyImpl } from "antlr4ts/VocabularyImpl";

import * as Utils from "antlr4ts/misc/Utils";

import { CompiscriptListener } from "./CompiscriptListener";
import { CompiscriptVisitor } from "./CompiscriptVisitor";


export class CompiscriptParser extends Parser {
	public static readonly T__0 = 1;
	public static readonly T__1 = 2;
	public static readonly T__2 = 3;
	public static readonly T__3 = 4;
	public static readonly T__4 = 5;
	public static readonly T__5 = 6;
	public static readonly T__6 = 7;
	public static readonly T__7 = 8;
	public static readonly T__8 = 9;
	public static readonly T__9 = 10;
	public static readonly T__10 = 11;
	public static readonly T__11 = 12;
	public static readonly T__12 = 13;
	public static readonly T__13 = 14;
	public static readonly T__14 = 15;
	public static readonly T__15 = 16;
	public static readonly T__16 = 17;
	public static readonly T__17 = 18;
	public static readonly T__18 = 19;
	public static readonly T__19 = 20;
	public static readonly T__20 = 21;
	public static readonly T__21 = 22;
	public static readonly T__22 = 23;
	public static readonly T__23 = 24;
	public static readonly T__24 = 25;
	public static readonly T__25 = 26;
	public static readonly T__26 = 27;
	public static readonly T__27 = 28;
	public static readonly T__28 = 29;
	public static readonly T__29 = 30;
	public static readonly T__30 = 31;
	public static readonly T__31 = 32;
	public static readonly T__32 = 33;
	public static readonly T__33 = 34;
	public static readonly T__34 = 35;
	public static readonly T__35 = 36;
	public static readonly T__36 = 37;
	public static readonly T__37 = 38;
	public static readonly T__38 = 39;
	public static readonly T__39 = 40;
	public static readonly T__40 = 41;
	public static readonly T__41 = 42;
	public static readonly T__42 = 43;
	public static readonly T__43 = 44;
	public static readonly T__44 = 45;
	public static readonly T__45 = 46;
	public static readonly T__46 = 47;
	public static readonly T__47 = 48;
	public static readonly T__48 = 49;
	public static readonly T__49 = 50;
	public static readonly T__50 = 51;
	public static readonly T__51 = 52;
	public static readonly T__52 = 53;
	public static readonly T__53 = 54;
	public static readonly T__54 = 55;
	public static readonly Literal = 56;
	public static readonly IntegerLiteral = 57;
	public static readonly StringLiteral = 58;
	public static readonly Identifier = 59;
	public static readonly WS = 60;
	public static readonly COMMENT = 61;
	public static readonly MULTILINE_COMMENT = 62;
	public static readonly RULE_program = 0;
	public static readonly RULE_statement = 1;
	public static readonly RULE_block = 2;
	public static readonly RULE_variableDeclaration = 3;
	public static readonly RULE_constantDeclaration = 4;
	public static readonly RULE_typeAnnotation = 5;
	public static readonly RULE_initializer = 6;
	public static readonly RULE_assignment = 7;
	public static readonly RULE_expressionStatement = 8;
	public static readonly RULE_printStatement = 9;
	public static readonly RULE_ifStatement = 10;
	public static readonly RULE_whileStatement = 11;
	public static readonly RULE_doWhileStatement = 12;
	public static readonly RULE_forStatement = 13;
	public static readonly RULE_foreachStatement = 14;
	public static readonly RULE_breakStatement = 15;
	public static readonly RULE_continueStatement = 16;
	public static readonly RULE_returnStatement = 17;
	public static readonly RULE_tryCatchStatement = 18;
	public static readonly RULE_switchStatement = 19;
	public static readonly RULE_switchCase = 20;
	public static readonly RULE_defaultCase = 21;
	public static readonly RULE_functionDeclaration = 22;
	public static readonly RULE_parameters = 23;
	public static readonly RULE_parameter = 24;
	public static readonly RULE_classDeclaration = 25;
	public static readonly RULE_classMember = 26;
	public static readonly RULE_expression = 27;
	public static readonly RULE_assignmentExpr = 28;
	public static readonly RULE_conditionalExpr = 29;
	public static readonly RULE_logicalOrExpr = 30;
	public static readonly RULE_logicalAndExpr = 31;
	public static readonly RULE_equalityExpr = 32;
	public static readonly RULE_relationalExpr = 33;
	public static readonly RULE_additiveExpr = 34;
	public static readonly RULE_multiplicativeExpr = 35;
	public static readonly RULE_unaryExpr = 36;
	public static readonly RULE_primaryExpr = 37;
	public static readonly RULE_literalExpr = 38;
	public static readonly RULE_leftHandSide = 39;
	public static readonly RULE_primaryAtom = 40;
	public static readonly RULE_suffixOp = 41;
	public static readonly RULE_arguments = 42;
	public static readonly RULE_arrayLiteral = 43;
	public static readonly RULE_type = 44;
	public static readonly RULE_baseType = 45;
	// tslint:disable:no-trailing-whitespace
	public static readonly ruleNames: string[] = [
		"program", "statement", "block", "variableDeclaration", "constantDeclaration", 
		"typeAnnotation", "initializer", "assignment", "expressionStatement", 
		"printStatement", "ifStatement", "whileStatement", "doWhileStatement", 
		"forStatement", "foreachStatement", "breakStatement", "continueStatement", 
		"returnStatement", "tryCatchStatement", "switchStatement", "switchCase", 
		"defaultCase", "functionDeclaration", "parameters", "parameter", "classDeclaration", 
		"classMember", "expression", "assignmentExpr", "conditionalExpr", "logicalOrExpr", 
		"logicalAndExpr", "equalityExpr", "relationalExpr", "additiveExpr", "multiplicativeExpr", 
		"unaryExpr", "primaryExpr", "literalExpr", "leftHandSide", "primaryAtom", 
		"suffixOp", "arguments", "arrayLiteral", "type", "baseType",
	];

	private static readonly _LITERAL_NAMES: Array<string | undefined> = [
		undefined, "'{'", "'}'", "'let'", "'var'", "';'", "'const'", "'='", "':'", 
		"'.'", "'print'", "'('", "')'", "'if'", "'else'", "'while'", "'do'", "'for'", 
		"'foreach'", "'in'", "'break'", "'continue'", "'return'", "'try'", "'catch'", 
		"'switch'", "'case'", "'default'", "'function'", "','", "'class'", "'?'", 
		"'||'", "'&&'", "'=='", "'!='", "'<'", "'<='", "'>'", "'>='", "'+'", "'-'", 
		"'*'", "'/'", "'%'", "'!'", "'null'", "'true'", "'false'", "'new'", "'this'", 
		"'['", "']'", "'boolean'", "'integer'", "'string'",
	];
	private static readonly _SYMBOLIC_NAMES: Array<string | undefined> = [
		undefined, undefined, undefined, undefined, undefined, undefined, undefined, 
		undefined, undefined, undefined, undefined, undefined, undefined, undefined, 
		undefined, undefined, undefined, undefined, undefined, undefined, undefined, 
		undefined, undefined, undefined, undefined, undefined, undefined, undefined, 
		undefined, undefined, undefined, undefined, undefined, undefined, undefined, 
		undefined, undefined, undefined, undefined, undefined, undefined, undefined, 
		undefined, undefined, undefined, undefined, undefined, undefined, undefined, 
		undefined, undefined, undefined, undefined, undefined, undefined, undefined, 
		"Literal", "IntegerLiteral", "StringLiteral", "Identifier", "WS", "COMMENT", 
		"MULTILINE_COMMENT",
	];
	public static readonly VOCABULARY: Vocabulary = new VocabularyImpl(CompiscriptParser._LITERAL_NAMES, CompiscriptParser._SYMBOLIC_NAMES, []);

	// @Override
	// @NotNull
	public get vocabulary(): Vocabulary {
		return CompiscriptParser.VOCABULARY;
	}
	// tslint:enable:no-trailing-whitespace

	// @Override
	public get grammarFileName(): string { return "Compiscript.g4"; }

	// @Override
	public get ruleNames(): string[] { return CompiscriptParser.ruleNames; }

	// @Override
	public get serializedATN(): string { return CompiscriptParser._serializedATN; }

	protected createFailedPredicateException(predicate?: string, message?: string): FailedPredicateException {
		return new FailedPredicateException(this, predicate, message);
	}

	constructor(input: TokenStream) {
		super(input);
		this._interp = new ParserATNSimulator(CompiscriptParser._ATN, this);
	}
	// @RuleVersion(0)
	public program(): ProgramContext {
		let _localctx: ProgramContext = new ProgramContext(this._ctx, this.state);
		this.enterRule(_localctx, 0, CompiscriptParser.RULE_program);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 95;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while ((((_la) & ~0x1F) === 0 && ((1 << _la) & ((1 << CompiscriptParser.T__0) | (1 << CompiscriptParser.T__2) | (1 << CompiscriptParser.T__3) | (1 << CompiscriptParser.T__5) | (1 << CompiscriptParser.T__9) | (1 << CompiscriptParser.T__10) | (1 << CompiscriptParser.T__12) | (1 << CompiscriptParser.T__14) | (1 << CompiscriptParser.T__15) | (1 << CompiscriptParser.T__16) | (1 << CompiscriptParser.T__17) | (1 << CompiscriptParser.T__19) | (1 << CompiscriptParser.T__20) | (1 << CompiscriptParser.T__21) | (1 << CompiscriptParser.T__22) | (1 << CompiscriptParser.T__24) | (1 << CompiscriptParser.T__27) | (1 << CompiscriptParser.T__29))) !== 0) || ((((_la - 41)) & ~0x1F) === 0 && ((1 << (_la - 41)) & ((1 << (CompiscriptParser.T__40 - 41)) | (1 << (CompiscriptParser.T__44 - 41)) | (1 << (CompiscriptParser.T__45 - 41)) | (1 << (CompiscriptParser.T__46 - 41)) | (1 << (CompiscriptParser.T__47 - 41)) | (1 << (CompiscriptParser.T__48 - 41)) | (1 << (CompiscriptParser.T__49 - 41)) | (1 << (CompiscriptParser.T__50 - 41)) | (1 << (CompiscriptParser.Literal - 41)) | (1 << (CompiscriptParser.Identifier - 41)))) !== 0)) {
				{
				{
				this.state = 92;
				this.statement();
				}
				}
				this.state = 97;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			this.state = 98;
			this.match(CompiscriptParser.EOF);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public statement(): StatementContext {
		let _localctx: StatementContext = new StatementContext(this._ctx, this.state);
		this.enterRule(_localctx, 2, CompiscriptParser.RULE_statement);
		try {
			this.state = 118;
			this._errHandler.sync(this);
			switch ( this.interpreter.adaptivePredict(this._input, 1, this._ctx) ) {
			case 1:
				this.enterOuterAlt(_localctx, 1);
				{
				this.state = 100;
				this.variableDeclaration();
				}
				break;

			case 2:
				this.enterOuterAlt(_localctx, 2);
				{
				this.state = 101;
				this.constantDeclaration();
				}
				break;

			case 3:
				this.enterOuterAlt(_localctx, 3);
				{
				this.state = 102;
				this.assignment();
				}
				break;

			case 4:
				this.enterOuterAlt(_localctx, 4);
				{
				this.state = 103;
				this.functionDeclaration();
				}
				break;

			case 5:
				this.enterOuterAlt(_localctx, 5);
				{
				this.state = 104;
				this.classDeclaration();
				}
				break;

			case 6:
				this.enterOuterAlt(_localctx, 6);
				{
				this.state = 105;
				this.expressionStatement();
				}
				break;

			case 7:
				this.enterOuterAlt(_localctx, 7);
				{
				this.state = 106;
				this.printStatement();
				}
				break;

			case 8:
				this.enterOuterAlt(_localctx, 8);
				{
				this.state = 107;
				this.block();
				}
				break;

			case 9:
				this.enterOuterAlt(_localctx, 9);
				{
				this.state = 108;
				this.ifStatement();
				}
				break;

			case 10:
				this.enterOuterAlt(_localctx, 10);
				{
				this.state = 109;
				this.whileStatement();
				}
				break;

			case 11:
				this.enterOuterAlt(_localctx, 11);
				{
				this.state = 110;
				this.doWhileStatement();
				}
				break;

			case 12:
				this.enterOuterAlt(_localctx, 12);
				{
				this.state = 111;
				this.forStatement();
				}
				break;

			case 13:
				this.enterOuterAlt(_localctx, 13);
				{
				this.state = 112;
				this.foreachStatement();
				}
				break;

			case 14:
				this.enterOuterAlt(_localctx, 14);
				{
				this.state = 113;
				this.tryCatchStatement();
				}
				break;

			case 15:
				this.enterOuterAlt(_localctx, 15);
				{
				this.state = 114;
				this.switchStatement();
				}
				break;

			case 16:
				this.enterOuterAlt(_localctx, 16);
				{
				this.state = 115;
				this.breakStatement();
				}
				break;

			case 17:
				this.enterOuterAlt(_localctx, 17);
				{
				this.state = 116;
				this.continueStatement();
				}
				break;

			case 18:
				this.enterOuterAlt(_localctx, 18);
				{
				this.state = 117;
				this.returnStatement();
				}
				break;
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public block(): BlockContext {
		let _localctx: BlockContext = new BlockContext(this._ctx, this.state);
		this.enterRule(_localctx, 4, CompiscriptParser.RULE_block);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 120;
			this.match(CompiscriptParser.T__0);
			this.state = 124;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while ((((_la) & ~0x1F) === 0 && ((1 << _la) & ((1 << CompiscriptParser.T__0) | (1 << CompiscriptParser.T__2) | (1 << CompiscriptParser.T__3) | (1 << CompiscriptParser.T__5) | (1 << CompiscriptParser.T__9) | (1 << CompiscriptParser.T__10) | (1 << CompiscriptParser.T__12) | (1 << CompiscriptParser.T__14) | (1 << CompiscriptParser.T__15) | (1 << CompiscriptParser.T__16) | (1 << CompiscriptParser.T__17) | (1 << CompiscriptParser.T__19) | (1 << CompiscriptParser.T__20) | (1 << CompiscriptParser.T__21) | (1 << CompiscriptParser.T__22) | (1 << CompiscriptParser.T__24) | (1 << CompiscriptParser.T__27) | (1 << CompiscriptParser.T__29))) !== 0) || ((((_la - 41)) & ~0x1F) === 0 && ((1 << (_la - 41)) & ((1 << (CompiscriptParser.T__40 - 41)) | (1 << (CompiscriptParser.T__44 - 41)) | (1 << (CompiscriptParser.T__45 - 41)) | (1 << (CompiscriptParser.T__46 - 41)) | (1 << (CompiscriptParser.T__47 - 41)) | (1 << (CompiscriptParser.T__48 - 41)) | (1 << (CompiscriptParser.T__49 - 41)) | (1 << (CompiscriptParser.T__50 - 41)) | (1 << (CompiscriptParser.Literal - 41)) | (1 << (CompiscriptParser.Identifier - 41)))) !== 0)) {
				{
				{
				this.state = 121;
				this.statement();
				}
				}
				this.state = 126;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			this.state = 127;
			this.match(CompiscriptParser.T__1);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public variableDeclaration(): VariableDeclarationContext {
		let _localctx: VariableDeclarationContext = new VariableDeclarationContext(this._ctx, this.state);
		this.enterRule(_localctx, 6, CompiscriptParser.RULE_variableDeclaration);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 129;
			_la = this._input.LA(1);
			if (!(_la === CompiscriptParser.T__2 || _la === CompiscriptParser.T__3)) {
			this._errHandler.recoverInline(this);
			} else {
				if (this._input.LA(1) === Token.EOF) {
					this.matchedEOF = true;
				}

				this._errHandler.reportMatch(this);
				this.consume();
			}
			this.state = 130;
			this.match(CompiscriptParser.Identifier);
			this.state = 132;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			if (_la === CompiscriptParser.T__7) {
				{
				this.state = 131;
				this.typeAnnotation();
				}
			}

			this.state = 135;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			if (_la === CompiscriptParser.T__6) {
				{
				this.state = 134;
				this.initializer();
				}
			}

			this.state = 137;
			this.match(CompiscriptParser.T__4);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public constantDeclaration(): ConstantDeclarationContext {
		let _localctx: ConstantDeclarationContext = new ConstantDeclarationContext(this._ctx, this.state);
		this.enterRule(_localctx, 8, CompiscriptParser.RULE_constantDeclaration);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 139;
			this.match(CompiscriptParser.T__5);
			this.state = 140;
			this.match(CompiscriptParser.Identifier);
			this.state = 142;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			if (_la === CompiscriptParser.T__7) {
				{
				this.state = 141;
				this.typeAnnotation();
				}
			}

			this.state = 144;
			this.match(CompiscriptParser.T__6);
			this.state = 145;
			this.expression();
			this.state = 146;
			this.match(CompiscriptParser.T__4);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public typeAnnotation(): TypeAnnotationContext {
		let _localctx: TypeAnnotationContext = new TypeAnnotationContext(this._ctx, this.state);
		this.enterRule(_localctx, 10, CompiscriptParser.RULE_typeAnnotation);
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 148;
			this.match(CompiscriptParser.T__7);
			this.state = 149;
			this.type();
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public initializer(): InitializerContext {
		let _localctx: InitializerContext = new InitializerContext(this._ctx, this.state);
		this.enterRule(_localctx, 12, CompiscriptParser.RULE_initializer);
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 151;
			this.match(CompiscriptParser.T__6);
			this.state = 152;
			this.expression();
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public assignment(): AssignmentContext {
		let _localctx: AssignmentContext = new AssignmentContext(this._ctx, this.state);
		this.enterRule(_localctx, 14, CompiscriptParser.RULE_assignment);
		try {
			this.state = 166;
			this._errHandler.sync(this);
			switch ( this.interpreter.adaptivePredict(this._input, 6, this._ctx) ) {
			case 1:
				this.enterOuterAlt(_localctx, 1);
				{
				this.state = 154;
				this.match(CompiscriptParser.Identifier);
				this.state = 155;
				this.match(CompiscriptParser.T__6);
				this.state = 156;
				this.expression();
				this.state = 157;
				this.match(CompiscriptParser.T__4);
				}
				break;

			case 2:
				this.enterOuterAlt(_localctx, 2);
				{
				this.state = 159;
				this.expression();
				this.state = 160;
				this.match(CompiscriptParser.T__8);
				this.state = 161;
				this.match(CompiscriptParser.Identifier);
				this.state = 162;
				this.match(CompiscriptParser.T__6);
				this.state = 163;
				this.expression();
				this.state = 164;
				this.match(CompiscriptParser.T__4);
				}
				break;
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public expressionStatement(): ExpressionStatementContext {
		let _localctx: ExpressionStatementContext = new ExpressionStatementContext(this._ctx, this.state);
		this.enterRule(_localctx, 16, CompiscriptParser.RULE_expressionStatement);
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 168;
			this.expression();
			this.state = 169;
			this.match(CompiscriptParser.T__4);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public printStatement(): PrintStatementContext {
		let _localctx: PrintStatementContext = new PrintStatementContext(this._ctx, this.state);
		this.enterRule(_localctx, 18, CompiscriptParser.RULE_printStatement);
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 171;
			this.match(CompiscriptParser.T__9);
			this.state = 172;
			this.match(CompiscriptParser.T__10);
			this.state = 173;
			this.expression();
			this.state = 174;
			this.match(CompiscriptParser.T__11);
			this.state = 175;
			this.match(CompiscriptParser.T__4);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public ifStatement(): IfStatementContext {
		let _localctx: IfStatementContext = new IfStatementContext(this._ctx, this.state);
		this.enterRule(_localctx, 20, CompiscriptParser.RULE_ifStatement);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 177;
			this.match(CompiscriptParser.T__12);
			this.state = 178;
			this.match(CompiscriptParser.T__10);
			this.state = 179;
			this.expression();
			this.state = 180;
			this.match(CompiscriptParser.T__11);
			this.state = 181;
			this.block();
			this.state = 184;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			if (_la === CompiscriptParser.T__13) {
				{
				this.state = 182;
				this.match(CompiscriptParser.T__13);
				this.state = 183;
				this.block();
				}
			}

			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public whileStatement(): WhileStatementContext {
		let _localctx: WhileStatementContext = new WhileStatementContext(this._ctx, this.state);
		this.enterRule(_localctx, 22, CompiscriptParser.RULE_whileStatement);
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 186;
			this.match(CompiscriptParser.T__14);
			this.state = 187;
			this.match(CompiscriptParser.T__10);
			this.state = 188;
			this.expression();
			this.state = 189;
			this.match(CompiscriptParser.T__11);
			this.state = 190;
			this.block();
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public doWhileStatement(): DoWhileStatementContext {
		let _localctx: DoWhileStatementContext = new DoWhileStatementContext(this._ctx, this.state);
		this.enterRule(_localctx, 24, CompiscriptParser.RULE_doWhileStatement);
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 192;
			this.match(CompiscriptParser.T__15);
			this.state = 193;
			this.block();
			this.state = 194;
			this.match(CompiscriptParser.T__14);
			this.state = 195;
			this.match(CompiscriptParser.T__10);
			this.state = 196;
			this.expression();
			this.state = 197;
			this.match(CompiscriptParser.T__11);
			this.state = 198;
			this.match(CompiscriptParser.T__4);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public forStatement(): ForStatementContext {
		let _localctx: ForStatementContext = new ForStatementContext(this._ctx, this.state);
		this.enterRule(_localctx, 26, CompiscriptParser.RULE_forStatement);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 200;
			this.match(CompiscriptParser.T__16);
			this.state = 201;
			this.match(CompiscriptParser.T__10);
			this.state = 205;
			this._errHandler.sync(this);
			switch (this._input.LA(1)) {
			case CompiscriptParser.T__2:
			case CompiscriptParser.T__3:
				{
				this.state = 202;
				this.variableDeclaration();
				}
				break;
			case CompiscriptParser.T__10:
			case CompiscriptParser.T__40:
			case CompiscriptParser.T__44:
			case CompiscriptParser.T__45:
			case CompiscriptParser.T__46:
			case CompiscriptParser.T__47:
			case CompiscriptParser.T__48:
			case CompiscriptParser.T__49:
			case CompiscriptParser.T__50:
			case CompiscriptParser.Literal:
			case CompiscriptParser.Identifier:
				{
				this.state = 203;
				this.assignment();
				}
				break;
			case CompiscriptParser.T__4:
				{
				this.state = 204;
				this.match(CompiscriptParser.T__4);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
			this.state = 208;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			if (_la === CompiscriptParser.T__10 || ((((_la - 41)) & ~0x1F) === 0 && ((1 << (_la - 41)) & ((1 << (CompiscriptParser.T__40 - 41)) | (1 << (CompiscriptParser.T__44 - 41)) | (1 << (CompiscriptParser.T__45 - 41)) | (1 << (CompiscriptParser.T__46 - 41)) | (1 << (CompiscriptParser.T__47 - 41)) | (1 << (CompiscriptParser.T__48 - 41)) | (1 << (CompiscriptParser.T__49 - 41)) | (1 << (CompiscriptParser.T__50 - 41)) | (1 << (CompiscriptParser.Literal - 41)) | (1 << (CompiscriptParser.Identifier - 41)))) !== 0)) {
				{
				this.state = 207;
				this.expression();
				}
			}

			this.state = 210;
			this.match(CompiscriptParser.T__4);
			this.state = 212;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			if (_la === CompiscriptParser.T__10 || ((((_la - 41)) & ~0x1F) === 0 && ((1 << (_la - 41)) & ((1 << (CompiscriptParser.T__40 - 41)) | (1 << (CompiscriptParser.T__44 - 41)) | (1 << (CompiscriptParser.T__45 - 41)) | (1 << (CompiscriptParser.T__46 - 41)) | (1 << (CompiscriptParser.T__47 - 41)) | (1 << (CompiscriptParser.T__48 - 41)) | (1 << (CompiscriptParser.T__49 - 41)) | (1 << (CompiscriptParser.T__50 - 41)) | (1 << (CompiscriptParser.Literal - 41)) | (1 << (CompiscriptParser.Identifier - 41)))) !== 0)) {
				{
				this.state = 211;
				this.expression();
				}
			}

			this.state = 214;
			this.match(CompiscriptParser.T__11);
			this.state = 215;
			this.block();
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public foreachStatement(): ForeachStatementContext {
		let _localctx: ForeachStatementContext = new ForeachStatementContext(this._ctx, this.state);
		this.enterRule(_localctx, 28, CompiscriptParser.RULE_foreachStatement);
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 217;
			this.match(CompiscriptParser.T__17);
			this.state = 218;
			this.match(CompiscriptParser.T__10);
			this.state = 219;
			this.match(CompiscriptParser.Identifier);
			this.state = 220;
			this.match(CompiscriptParser.T__18);
			this.state = 221;
			this.expression();
			this.state = 222;
			this.match(CompiscriptParser.T__11);
			this.state = 223;
			this.block();
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public breakStatement(): BreakStatementContext {
		let _localctx: BreakStatementContext = new BreakStatementContext(this._ctx, this.state);
		this.enterRule(_localctx, 30, CompiscriptParser.RULE_breakStatement);
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 225;
			this.match(CompiscriptParser.T__19);
			this.state = 226;
			this.match(CompiscriptParser.T__4);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public continueStatement(): ContinueStatementContext {
		let _localctx: ContinueStatementContext = new ContinueStatementContext(this._ctx, this.state);
		this.enterRule(_localctx, 32, CompiscriptParser.RULE_continueStatement);
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 228;
			this.match(CompiscriptParser.T__20);
			this.state = 229;
			this.match(CompiscriptParser.T__4);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public returnStatement(): ReturnStatementContext {
		let _localctx: ReturnStatementContext = new ReturnStatementContext(this._ctx, this.state);
		this.enterRule(_localctx, 34, CompiscriptParser.RULE_returnStatement);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 231;
			this.match(CompiscriptParser.T__21);
			this.state = 233;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			if (_la === CompiscriptParser.T__10 || ((((_la - 41)) & ~0x1F) === 0 && ((1 << (_la - 41)) & ((1 << (CompiscriptParser.T__40 - 41)) | (1 << (CompiscriptParser.T__44 - 41)) | (1 << (CompiscriptParser.T__45 - 41)) | (1 << (CompiscriptParser.T__46 - 41)) | (1 << (CompiscriptParser.T__47 - 41)) | (1 << (CompiscriptParser.T__48 - 41)) | (1 << (CompiscriptParser.T__49 - 41)) | (1 << (CompiscriptParser.T__50 - 41)) | (1 << (CompiscriptParser.Literal - 41)) | (1 << (CompiscriptParser.Identifier - 41)))) !== 0)) {
				{
				this.state = 232;
				this.expression();
				}
			}

			this.state = 235;
			this.match(CompiscriptParser.T__4);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public tryCatchStatement(): TryCatchStatementContext {
		let _localctx: TryCatchStatementContext = new TryCatchStatementContext(this._ctx, this.state);
		this.enterRule(_localctx, 36, CompiscriptParser.RULE_tryCatchStatement);
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 237;
			this.match(CompiscriptParser.T__22);
			this.state = 238;
			this.block();
			this.state = 239;
			this.match(CompiscriptParser.T__23);
			this.state = 240;
			this.match(CompiscriptParser.T__10);
			this.state = 241;
			this.match(CompiscriptParser.Identifier);
			this.state = 242;
			this.match(CompiscriptParser.T__11);
			this.state = 243;
			this.block();
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public switchStatement(): SwitchStatementContext {
		let _localctx: SwitchStatementContext = new SwitchStatementContext(this._ctx, this.state);
		this.enterRule(_localctx, 38, CompiscriptParser.RULE_switchStatement);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 245;
			this.match(CompiscriptParser.T__24);
			this.state = 246;
			this.match(CompiscriptParser.T__10);
			this.state = 247;
			this.expression();
			this.state = 248;
			this.match(CompiscriptParser.T__11);
			this.state = 249;
			this.match(CompiscriptParser.T__0);
			this.state = 253;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while (_la === CompiscriptParser.T__25) {
				{
				{
				this.state = 250;
				this.switchCase();
				}
				}
				this.state = 255;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			this.state = 257;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			if (_la === CompiscriptParser.T__26) {
				{
				this.state = 256;
				this.defaultCase();
				}
			}

			this.state = 259;
			this.match(CompiscriptParser.T__1);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public switchCase(): SwitchCaseContext {
		let _localctx: SwitchCaseContext = new SwitchCaseContext(this._ctx, this.state);
		this.enterRule(_localctx, 40, CompiscriptParser.RULE_switchCase);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 261;
			this.match(CompiscriptParser.T__25);
			this.state = 262;
			this.expression();
			this.state = 263;
			this.match(CompiscriptParser.T__7);
			this.state = 267;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while ((((_la) & ~0x1F) === 0 && ((1 << _la) & ((1 << CompiscriptParser.T__0) | (1 << CompiscriptParser.T__2) | (1 << CompiscriptParser.T__3) | (1 << CompiscriptParser.T__5) | (1 << CompiscriptParser.T__9) | (1 << CompiscriptParser.T__10) | (1 << CompiscriptParser.T__12) | (1 << CompiscriptParser.T__14) | (1 << CompiscriptParser.T__15) | (1 << CompiscriptParser.T__16) | (1 << CompiscriptParser.T__17) | (1 << CompiscriptParser.T__19) | (1 << CompiscriptParser.T__20) | (1 << CompiscriptParser.T__21) | (1 << CompiscriptParser.T__22) | (1 << CompiscriptParser.T__24) | (1 << CompiscriptParser.T__27) | (1 << CompiscriptParser.T__29))) !== 0) || ((((_la - 41)) & ~0x1F) === 0 && ((1 << (_la - 41)) & ((1 << (CompiscriptParser.T__40 - 41)) | (1 << (CompiscriptParser.T__44 - 41)) | (1 << (CompiscriptParser.T__45 - 41)) | (1 << (CompiscriptParser.T__46 - 41)) | (1 << (CompiscriptParser.T__47 - 41)) | (1 << (CompiscriptParser.T__48 - 41)) | (1 << (CompiscriptParser.T__49 - 41)) | (1 << (CompiscriptParser.T__50 - 41)) | (1 << (CompiscriptParser.Literal - 41)) | (1 << (CompiscriptParser.Identifier - 41)))) !== 0)) {
				{
				{
				this.state = 264;
				this.statement();
				}
				}
				this.state = 269;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public defaultCase(): DefaultCaseContext {
		let _localctx: DefaultCaseContext = new DefaultCaseContext(this._ctx, this.state);
		this.enterRule(_localctx, 42, CompiscriptParser.RULE_defaultCase);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 270;
			this.match(CompiscriptParser.T__26);
			this.state = 271;
			this.match(CompiscriptParser.T__7);
			this.state = 275;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while ((((_la) & ~0x1F) === 0 && ((1 << _la) & ((1 << CompiscriptParser.T__0) | (1 << CompiscriptParser.T__2) | (1 << CompiscriptParser.T__3) | (1 << CompiscriptParser.T__5) | (1 << CompiscriptParser.T__9) | (1 << CompiscriptParser.T__10) | (1 << CompiscriptParser.T__12) | (1 << CompiscriptParser.T__14) | (1 << CompiscriptParser.T__15) | (1 << CompiscriptParser.T__16) | (1 << CompiscriptParser.T__17) | (1 << CompiscriptParser.T__19) | (1 << CompiscriptParser.T__20) | (1 << CompiscriptParser.T__21) | (1 << CompiscriptParser.T__22) | (1 << CompiscriptParser.T__24) | (1 << CompiscriptParser.T__27) | (1 << CompiscriptParser.T__29))) !== 0) || ((((_la - 41)) & ~0x1F) === 0 && ((1 << (_la - 41)) & ((1 << (CompiscriptParser.T__40 - 41)) | (1 << (CompiscriptParser.T__44 - 41)) | (1 << (CompiscriptParser.T__45 - 41)) | (1 << (CompiscriptParser.T__46 - 41)) | (1 << (CompiscriptParser.T__47 - 41)) | (1 << (CompiscriptParser.T__48 - 41)) | (1 << (CompiscriptParser.T__49 - 41)) | (1 << (CompiscriptParser.T__50 - 41)) | (1 << (CompiscriptParser.Literal - 41)) | (1 << (CompiscriptParser.Identifier - 41)))) !== 0)) {
				{
				{
				this.state = 272;
				this.statement();
				}
				}
				this.state = 277;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public functionDeclaration(): FunctionDeclarationContext {
		let _localctx: FunctionDeclarationContext = new FunctionDeclarationContext(this._ctx, this.state);
		this.enterRule(_localctx, 44, CompiscriptParser.RULE_functionDeclaration);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 278;
			this.match(CompiscriptParser.T__27);
			this.state = 279;
			this.match(CompiscriptParser.Identifier);
			this.state = 280;
			this.match(CompiscriptParser.T__10);
			this.state = 282;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			if (_la === CompiscriptParser.Identifier) {
				{
				this.state = 281;
				this.parameters();
				}
			}

			this.state = 284;
			this.match(CompiscriptParser.T__11);
			this.state = 287;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			if (_la === CompiscriptParser.T__7) {
				{
				this.state = 285;
				this.match(CompiscriptParser.T__7);
				this.state = 286;
				this.type();
				}
			}

			this.state = 289;
			this.block();
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public parameters(): ParametersContext {
		let _localctx: ParametersContext = new ParametersContext(this._ctx, this.state);
		this.enterRule(_localctx, 46, CompiscriptParser.RULE_parameters);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 291;
			this.parameter();
			this.state = 296;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while (_la === CompiscriptParser.T__28) {
				{
				{
				this.state = 292;
				this.match(CompiscriptParser.T__28);
				this.state = 293;
				this.parameter();
				}
				}
				this.state = 298;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public parameter(): ParameterContext {
		let _localctx: ParameterContext = new ParameterContext(this._ctx, this.state);
		this.enterRule(_localctx, 48, CompiscriptParser.RULE_parameter);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 299;
			this.match(CompiscriptParser.Identifier);
			this.state = 302;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			if (_la === CompiscriptParser.T__7) {
				{
				this.state = 300;
				this.match(CompiscriptParser.T__7);
				this.state = 301;
				this.type();
				}
			}

			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public classDeclaration(): ClassDeclarationContext {
		let _localctx: ClassDeclarationContext = new ClassDeclarationContext(this._ctx, this.state);
		this.enterRule(_localctx, 50, CompiscriptParser.RULE_classDeclaration);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 304;
			this.match(CompiscriptParser.T__29);
			this.state = 305;
			this.match(CompiscriptParser.Identifier);
			this.state = 308;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			if (_la === CompiscriptParser.T__7) {
				{
				this.state = 306;
				this.match(CompiscriptParser.T__7);
				this.state = 307;
				this.match(CompiscriptParser.Identifier);
				}
			}

			this.state = 310;
			this.match(CompiscriptParser.T__0);
			this.state = 314;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while ((((_la) & ~0x1F) === 0 && ((1 << _la) & ((1 << CompiscriptParser.T__2) | (1 << CompiscriptParser.T__3) | (1 << CompiscriptParser.T__5) | (1 << CompiscriptParser.T__27))) !== 0)) {
				{
				{
				this.state = 311;
				this.classMember();
				}
				}
				this.state = 316;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			this.state = 317;
			this.match(CompiscriptParser.T__1);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public classMember(): ClassMemberContext {
		let _localctx: ClassMemberContext = new ClassMemberContext(this._ctx, this.state);
		this.enterRule(_localctx, 52, CompiscriptParser.RULE_classMember);
		try {
			this.state = 322;
			this._errHandler.sync(this);
			switch (this._input.LA(1)) {
			case CompiscriptParser.T__27:
				this.enterOuterAlt(_localctx, 1);
				{
				this.state = 319;
				this.functionDeclaration();
				}
				break;
			case CompiscriptParser.T__2:
			case CompiscriptParser.T__3:
				this.enterOuterAlt(_localctx, 2);
				{
				this.state = 320;
				this.variableDeclaration();
				}
				break;
			case CompiscriptParser.T__5:
				this.enterOuterAlt(_localctx, 3);
				{
				this.state = 321;
				this.constantDeclaration();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public expression(): ExpressionContext {
		let _localctx: ExpressionContext = new ExpressionContext(this._ctx, this.state);
		this.enterRule(_localctx, 54, CompiscriptParser.RULE_expression);
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 324;
			this.assignmentExpr();
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public assignmentExpr(): AssignmentExprContext {
		let _localctx: AssignmentExprContext = new AssignmentExprContext(this._ctx, this.state);
		this.enterRule(_localctx, 56, CompiscriptParser.RULE_assignmentExpr);
		try {
			this.state = 337;
			this._errHandler.sync(this);
			switch ( this.interpreter.adaptivePredict(this._input, 23, this._ctx) ) {
			case 1:
				_localctx = new AssignExprContext(_localctx);
				this.enterOuterAlt(_localctx, 1);
				{
				this.state = 326;
				(_localctx as AssignExprContext)._lhs = this.leftHandSide();
				this.state = 327;
				this.match(CompiscriptParser.T__6);
				this.state = 328;
				this.assignmentExpr();
				}
				break;

			case 2:
				_localctx = new PropertyAssignExprContext(_localctx);
				this.enterOuterAlt(_localctx, 2);
				{
				this.state = 330;
				(_localctx as PropertyAssignExprContext)._lhs = this.leftHandSide();
				this.state = 331;
				this.match(CompiscriptParser.T__8);
				this.state = 332;
				this.match(CompiscriptParser.Identifier);
				this.state = 333;
				this.match(CompiscriptParser.T__6);
				this.state = 334;
				this.assignmentExpr();
				}
				break;

			case 3:
				_localctx = new ExprNoAssignContext(_localctx);
				this.enterOuterAlt(_localctx, 3);
				{
				this.state = 336;
				this.conditionalExpr();
				}
				break;
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public conditionalExpr(): ConditionalExprContext {
		let _localctx: ConditionalExprContext = new ConditionalExprContext(this._ctx, this.state);
		this.enterRule(_localctx, 58, CompiscriptParser.RULE_conditionalExpr);
		let _la: number;
		try {
			_localctx = new TernaryExprContext(_localctx);
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 339;
			this.logicalOrExpr();
			this.state = 345;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			if (_la === CompiscriptParser.T__30) {
				{
				this.state = 340;
				this.match(CompiscriptParser.T__30);
				this.state = 341;
				this.expression();
				this.state = 342;
				this.match(CompiscriptParser.T__7);
				this.state = 343;
				this.expression();
				}
			}

			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public logicalOrExpr(): LogicalOrExprContext {
		let _localctx: LogicalOrExprContext = new LogicalOrExprContext(this._ctx, this.state);
		this.enterRule(_localctx, 60, CompiscriptParser.RULE_logicalOrExpr);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 347;
			this.logicalAndExpr();
			this.state = 352;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while (_la === CompiscriptParser.T__31) {
				{
				{
				this.state = 348;
				this.match(CompiscriptParser.T__31);
				this.state = 349;
				this.logicalAndExpr();
				}
				}
				this.state = 354;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public logicalAndExpr(): LogicalAndExprContext {
		let _localctx: LogicalAndExprContext = new LogicalAndExprContext(this._ctx, this.state);
		this.enterRule(_localctx, 62, CompiscriptParser.RULE_logicalAndExpr);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 355;
			this.equalityExpr();
			this.state = 360;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while (_la === CompiscriptParser.T__32) {
				{
				{
				this.state = 356;
				this.match(CompiscriptParser.T__32);
				this.state = 357;
				this.equalityExpr();
				}
				}
				this.state = 362;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public equalityExpr(): EqualityExprContext {
		let _localctx: EqualityExprContext = new EqualityExprContext(this._ctx, this.state);
		this.enterRule(_localctx, 64, CompiscriptParser.RULE_equalityExpr);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 363;
			this.relationalExpr();
			this.state = 368;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while (_la === CompiscriptParser.T__33 || _la === CompiscriptParser.T__34) {
				{
				{
				this.state = 364;
				_la = this._input.LA(1);
				if (!(_la === CompiscriptParser.T__33 || _la === CompiscriptParser.T__34)) {
				this._errHandler.recoverInline(this);
				} else {
					if (this._input.LA(1) === Token.EOF) {
						this.matchedEOF = true;
					}

					this._errHandler.reportMatch(this);
					this.consume();
				}
				this.state = 365;
				this.relationalExpr();
				}
				}
				this.state = 370;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public relationalExpr(): RelationalExprContext {
		let _localctx: RelationalExprContext = new RelationalExprContext(this._ctx, this.state);
		this.enterRule(_localctx, 66, CompiscriptParser.RULE_relationalExpr);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 371;
			this.additiveExpr();
			this.state = 376;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while (((((_la - 36)) & ~0x1F) === 0 && ((1 << (_la - 36)) & ((1 << (CompiscriptParser.T__35 - 36)) | (1 << (CompiscriptParser.T__36 - 36)) | (1 << (CompiscriptParser.T__37 - 36)) | (1 << (CompiscriptParser.T__38 - 36)))) !== 0)) {
				{
				{
				this.state = 372;
				_la = this._input.LA(1);
				if (!(((((_la - 36)) & ~0x1F) === 0 && ((1 << (_la - 36)) & ((1 << (CompiscriptParser.T__35 - 36)) | (1 << (CompiscriptParser.T__36 - 36)) | (1 << (CompiscriptParser.T__37 - 36)) | (1 << (CompiscriptParser.T__38 - 36)))) !== 0))) {
				this._errHandler.recoverInline(this);
				} else {
					if (this._input.LA(1) === Token.EOF) {
						this.matchedEOF = true;
					}

					this._errHandler.reportMatch(this);
					this.consume();
				}
				this.state = 373;
				this.additiveExpr();
				}
				}
				this.state = 378;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public additiveExpr(): AdditiveExprContext {
		let _localctx: AdditiveExprContext = new AdditiveExprContext(this._ctx, this.state);
		this.enterRule(_localctx, 68, CompiscriptParser.RULE_additiveExpr);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 379;
			this.multiplicativeExpr();
			this.state = 384;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while (_la === CompiscriptParser.T__39 || _la === CompiscriptParser.T__40) {
				{
				{
				this.state = 380;
				_la = this._input.LA(1);
				if (!(_la === CompiscriptParser.T__39 || _la === CompiscriptParser.T__40)) {
				this._errHandler.recoverInline(this);
				} else {
					if (this._input.LA(1) === Token.EOF) {
						this.matchedEOF = true;
					}

					this._errHandler.reportMatch(this);
					this.consume();
				}
				this.state = 381;
				this.multiplicativeExpr();
				}
				}
				this.state = 386;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public multiplicativeExpr(): MultiplicativeExprContext {
		let _localctx: MultiplicativeExprContext = new MultiplicativeExprContext(this._ctx, this.state);
		this.enterRule(_localctx, 70, CompiscriptParser.RULE_multiplicativeExpr);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 387;
			this.unaryExpr();
			this.state = 392;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while (((((_la - 42)) & ~0x1F) === 0 && ((1 << (_la - 42)) & ((1 << (CompiscriptParser.T__41 - 42)) | (1 << (CompiscriptParser.T__42 - 42)) | (1 << (CompiscriptParser.T__43 - 42)))) !== 0)) {
				{
				{
				this.state = 388;
				_la = this._input.LA(1);
				if (!(((((_la - 42)) & ~0x1F) === 0 && ((1 << (_la - 42)) & ((1 << (CompiscriptParser.T__41 - 42)) | (1 << (CompiscriptParser.T__42 - 42)) | (1 << (CompiscriptParser.T__43 - 42)))) !== 0))) {
				this._errHandler.recoverInline(this);
				} else {
					if (this._input.LA(1) === Token.EOF) {
						this.matchedEOF = true;
					}

					this._errHandler.reportMatch(this);
					this.consume();
				}
				this.state = 389;
				this.unaryExpr();
				}
				}
				this.state = 394;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public unaryExpr(): UnaryExprContext {
		let _localctx: UnaryExprContext = new UnaryExprContext(this._ctx, this.state);
		this.enterRule(_localctx, 72, CompiscriptParser.RULE_unaryExpr);
		let _la: number;
		try {
			this.state = 398;
			this._errHandler.sync(this);
			switch (this._input.LA(1)) {
			case CompiscriptParser.T__40:
			case CompiscriptParser.T__44:
				this.enterOuterAlt(_localctx, 1);
				{
				this.state = 395;
				_la = this._input.LA(1);
				if (!(_la === CompiscriptParser.T__40 || _la === CompiscriptParser.T__44)) {
				this._errHandler.recoverInline(this);
				} else {
					if (this._input.LA(1) === Token.EOF) {
						this.matchedEOF = true;
					}

					this._errHandler.reportMatch(this);
					this.consume();
				}
				this.state = 396;
				this.unaryExpr();
				}
				break;
			case CompiscriptParser.T__10:
			case CompiscriptParser.T__45:
			case CompiscriptParser.T__46:
			case CompiscriptParser.T__47:
			case CompiscriptParser.T__48:
			case CompiscriptParser.T__49:
			case CompiscriptParser.T__50:
			case CompiscriptParser.Literal:
			case CompiscriptParser.Identifier:
				this.enterOuterAlt(_localctx, 2);
				{
				this.state = 397;
				this.primaryExpr();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public primaryExpr(): PrimaryExprContext {
		let _localctx: PrimaryExprContext = new PrimaryExprContext(this._ctx, this.state);
		this.enterRule(_localctx, 74, CompiscriptParser.RULE_primaryExpr);
		try {
			this.state = 406;
			this._errHandler.sync(this);
			switch (this._input.LA(1)) {
			case CompiscriptParser.T__45:
			case CompiscriptParser.T__46:
			case CompiscriptParser.T__47:
			case CompiscriptParser.T__50:
			case CompiscriptParser.Literal:
				this.enterOuterAlt(_localctx, 1);
				{
				this.state = 400;
				this.literalExpr();
				}
				break;
			case CompiscriptParser.T__48:
			case CompiscriptParser.T__49:
			case CompiscriptParser.Identifier:
				this.enterOuterAlt(_localctx, 2);
				{
				this.state = 401;
				this.leftHandSide();
				}
				break;
			case CompiscriptParser.T__10:
				this.enterOuterAlt(_localctx, 3);
				{
				this.state = 402;
				this.match(CompiscriptParser.T__10);
				this.state = 403;
				this.expression();
				this.state = 404;
				this.match(CompiscriptParser.T__11);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public literalExpr(): LiteralExprContext {
		let _localctx: LiteralExprContext = new LiteralExprContext(this._ctx, this.state);
		this.enterRule(_localctx, 76, CompiscriptParser.RULE_literalExpr);
		try {
			this.state = 413;
			this._errHandler.sync(this);
			switch (this._input.LA(1)) {
			case CompiscriptParser.Literal:
				this.enterOuterAlt(_localctx, 1);
				{
				this.state = 408;
				this.match(CompiscriptParser.Literal);
				}
				break;
			case CompiscriptParser.T__50:
				this.enterOuterAlt(_localctx, 2);
				{
				this.state = 409;
				this.arrayLiteral();
				}
				break;
			case CompiscriptParser.T__45:
				this.enterOuterAlt(_localctx, 3);
				{
				this.state = 410;
				this.match(CompiscriptParser.T__45);
				}
				break;
			case CompiscriptParser.T__46:
				this.enterOuterAlt(_localctx, 4);
				{
				this.state = 411;
				this.match(CompiscriptParser.T__46);
				}
				break;
			case CompiscriptParser.T__47:
				this.enterOuterAlt(_localctx, 5);
				{
				this.state = 412;
				this.match(CompiscriptParser.T__47);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public leftHandSide(): LeftHandSideContext {
		let _localctx: LeftHandSideContext = new LeftHandSideContext(this._ctx, this.state);
		this.enterRule(_localctx, 78, CompiscriptParser.RULE_leftHandSide);
		try {
			let _alt: number;
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 415;
			this.primaryAtom();
			this.state = 419;
			this._errHandler.sync(this);
			_alt = this.interpreter.adaptivePredict(this._input, 34, this._ctx);
			while (_alt !== 2 && _alt !== ATN.INVALID_ALT_NUMBER) {
				if (_alt === 1) {
					{
					{
					this.state = 416;
					this.suffixOp();
					}
					}
				}
				this.state = 421;
				this._errHandler.sync(this);
				_alt = this.interpreter.adaptivePredict(this._input, 34, this._ctx);
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public primaryAtom(): PrimaryAtomContext {
		let _localctx: PrimaryAtomContext = new PrimaryAtomContext(this._ctx, this.state);
		this.enterRule(_localctx, 80, CompiscriptParser.RULE_primaryAtom);
		let _la: number;
		try {
			this.state = 431;
			this._errHandler.sync(this);
			switch (this._input.LA(1)) {
			case CompiscriptParser.Identifier:
				_localctx = new IdentifierExprContext(_localctx);
				this.enterOuterAlt(_localctx, 1);
				{
				this.state = 422;
				this.match(CompiscriptParser.Identifier);
				}
				break;
			case CompiscriptParser.T__48:
				_localctx = new NewExprContext(_localctx);
				this.enterOuterAlt(_localctx, 2);
				{
				this.state = 423;
				this.match(CompiscriptParser.T__48);
				this.state = 424;
				this.match(CompiscriptParser.Identifier);
				this.state = 425;
				this.match(CompiscriptParser.T__10);
				this.state = 427;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
				if (_la === CompiscriptParser.T__10 || ((((_la - 41)) & ~0x1F) === 0 && ((1 << (_la - 41)) & ((1 << (CompiscriptParser.T__40 - 41)) | (1 << (CompiscriptParser.T__44 - 41)) | (1 << (CompiscriptParser.T__45 - 41)) | (1 << (CompiscriptParser.T__46 - 41)) | (1 << (CompiscriptParser.T__47 - 41)) | (1 << (CompiscriptParser.T__48 - 41)) | (1 << (CompiscriptParser.T__49 - 41)) | (1 << (CompiscriptParser.T__50 - 41)) | (1 << (CompiscriptParser.Literal - 41)) | (1 << (CompiscriptParser.Identifier - 41)))) !== 0)) {
					{
					this.state = 426;
					this.arguments();
					}
				}

				this.state = 429;
				this.match(CompiscriptParser.T__11);
				}
				break;
			case CompiscriptParser.T__49:
				_localctx = new ThisExprContext(_localctx);
				this.enterOuterAlt(_localctx, 3);
				{
				this.state = 430;
				this.match(CompiscriptParser.T__49);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public suffixOp(): SuffixOpContext {
		let _localctx: SuffixOpContext = new SuffixOpContext(this._ctx, this.state);
		this.enterRule(_localctx, 82, CompiscriptParser.RULE_suffixOp);
		let _la: number;
		try {
			this.state = 444;
			this._errHandler.sync(this);
			switch (this._input.LA(1)) {
			case CompiscriptParser.T__10:
				_localctx = new CallExprContext(_localctx);
				this.enterOuterAlt(_localctx, 1);
				{
				this.state = 433;
				this.match(CompiscriptParser.T__10);
				this.state = 435;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
				if (_la === CompiscriptParser.T__10 || ((((_la - 41)) & ~0x1F) === 0 && ((1 << (_la - 41)) & ((1 << (CompiscriptParser.T__40 - 41)) | (1 << (CompiscriptParser.T__44 - 41)) | (1 << (CompiscriptParser.T__45 - 41)) | (1 << (CompiscriptParser.T__46 - 41)) | (1 << (CompiscriptParser.T__47 - 41)) | (1 << (CompiscriptParser.T__48 - 41)) | (1 << (CompiscriptParser.T__49 - 41)) | (1 << (CompiscriptParser.T__50 - 41)) | (1 << (CompiscriptParser.Literal - 41)) | (1 << (CompiscriptParser.Identifier - 41)))) !== 0)) {
					{
					this.state = 434;
					this.arguments();
					}
				}

				this.state = 437;
				this.match(CompiscriptParser.T__11);
				}
				break;
			case CompiscriptParser.T__50:
				_localctx = new IndexExprContext(_localctx);
				this.enterOuterAlt(_localctx, 2);
				{
				this.state = 438;
				this.match(CompiscriptParser.T__50);
				this.state = 439;
				this.expression();
				this.state = 440;
				this.match(CompiscriptParser.T__51);
				}
				break;
			case CompiscriptParser.T__8:
				_localctx = new PropertyAccessExprContext(_localctx);
				this.enterOuterAlt(_localctx, 3);
				{
				this.state = 442;
				this.match(CompiscriptParser.T__8);
				this.state = 443;
				this.match(CompiscriptParser.Identifier);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public arguments(): ArgumentsContext {
		let _localctx: ArgumentsContext = new ArgumentsContext(this._ctx, this.state);
		this.enterRule(_localctx, 84, CompiscriptParser.RULE_arguments);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 446;
			this.expression();
			this.state = 451;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while (_la === CompiscriptParser.T__28) {
				{
				{
				this.state = 447;
				this.match(CompiscriptParser.T__28);
				this.state = 448;
				this.expression();
				}
				}
				this.state = 453;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public arrayLiteral(): ArrayLiteralContext {
		let _localctx: ArrayLiteralContext = new ArrayLiteralContext(this._ctx, this.state);
		this.enterRule(_localctx, 86, CompiscriptParser.RULE_arrayLiteral);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 454;
			this.match(CompiscriptParser.T__50);
			this.state = 463;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			if (_la === CompiscriptParser.T__10 || ((((_la - 41)) & ~0x1F) === 0 && ((1 << (_la - 41)) & ((1 << (CompiscriptParser.T__40 - 41)) | (1 << (CompiscriptParser.T__44 - 41)) | (1 << (CompiscriptParser.T__45 - 41)) | (1 << (CompiscriptParser.T__46 - 41)) | (1 << (CompiscriptParser.T__47 - 41)) | (1 << (CompiscriptParser.T__48 - 41)) | (1 << (CompiscriptParser.T__49 - 41)) | (1 << (CompiscriptParser.T__50 - 41)) | (1 << (CompiscriptParser.Literal - 41)) | (1 << (CompiscriptParser.Identifier - 41)))) !== 0)) {
				{
				this.state = 455;
				this.expression();
				this.state = 460;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
				while (_la === CompiscriptParser.T__28) {
					{
					{
					this.state = 456;
					this.match(CompiscriptParser.T__28);
					this.state = 457;
					this.expression();
					}
					}
					this.state = 462;
					this._errHandler.sync(this);
					_la = this._input.LA(1);
				}
				}
			}

			this.state = 465;
			this.match(CompiscriptParser.T__51);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public type(): TypeContext {
		let _localctx: TypeContext = new TypeContext(this._ctx, this.state);
		this.enterRule(_localctx, 88, CompiscriptParser.RULE_type);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 467;
			this.baseType();
			this.state = 472;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while (_la === CompiscriptParser.T__50) {
				{
				{
				this.state = 468;
				this.match(CompiscriptParser.T__50);
				this.state = 469;
				this.match(CompiscriptParser.T__51);
				}
				}
				this.state = 474;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}
	// @RuleVersion(0)
	public baseType(): BaseTypeContext {
		let _localctx: BaseTypeContext = new BaseTypeContext(this._ctx, this.state);
		this.enterRule(_localctx, 90, CompiscriptParser.RULE_baseType);
		let _la: number;
		try {
			this.enterOuterAlt(_localctx, 1);
			{
			this.state = 475;
			_la = this._input.LA(1);
			if (!(((((_la - 53)) & ~0x1F) === 0 && ((1 << (_la - 53)) & ((1 << (CompiscriptParser.T__52 - 53)) | (1 << (CompiscriptParser.T__53 - 53)) | (1 << (CompiscriptParser.T__54 - 53)) | (1 << (CompiscriptParser.Identifier - 53)))) !== 0))) {
			this._errHandler.recoverInline(this);
			} else {
				if (this._input.LA(1) === Token.EOF) {
					this.matchedEOF = true;
				}

				this._errHandler.reportMatch(this);
				this.consume();
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				_localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return _localctx;
	}

	public static readonly _serializedATN: string =
		"\x03\uC91D\uCABA\u058D\uAFBA\u4F53\u0607\uEA8B\uC241\x03@\u01E0\x04\x02" +
		"\t\x02\x04\x03\t\x03\x04\x04\t\x04\x04\x05\t\x05\x04\x06\t\x06\x04\x07" +
		"\t\x07\x04\b\t\b\x04\t\t\t\x04\n\t\n\x04\v\t\v\x04\f\t\f\x04\r\t\r\x04" +
		"\x0E\t\x0E\x04\x0F\t\x0F\x04\x10\t\x10\x04\x11\t\x11\x04\x12\t\x12\x04" +
		"\x13\t\x13\x04\x14\t\x14\x04\x15\t\x15\x04\x16\t\x16\x04\x17\t\x17\x04" +
		"\x18\t\x18\x04\x19\t\x19\x04\x1A\t\x1A\x04\x1B\t\x1B\x04\x1C\t\x1C\x04" +
		"\x1D\t\x1D\x04\x1E\t\x1E\x04\x1F\t\x1F\x04 \t \x04!\t!\x04\"\t\"\x04#" +
		"\t#\x04$\t$\x04%\t%\x04&\t&\x04\'\t\'\x04(\t(\x04)\t)\x04*\t*\x04+\t+" +
		"\x04,\t,\x04-\t-\x04.\t.\x04/\t/\x03\x02\x07\x02`\n\x02\f\x02\x0E\x02" +
		"c\v\x02\x03\x02\x03\x02\x03\x03\x03\x03\x03\x03\x03\x03\x03\x03\x03\x03" +
		"\x03\x03\x03\x03\x03\x03\x03\x03\x03\x03\x03\x03\x03\x03\x03\x03\x03\x03" +
		"\x03\x03\x03\x03\x03\x03\x05\x03y\n\x03\x03\x04\x03\x04\x07\x04}\n\x04" +
		"\f\x04\x0E\x04\x80\v\x04\x03\x04\x03\x04\x03\x05\x03\x05\x03\x05\x05\x05" +
		"\x87\n\x05\x03\x05\x05\x05\x8A\n\x05\x03\x05\x03\x05\x03\x06\x03\x06\x03" +
		"\x06\x05\x06\x91\n\x06\x03\x06\x03\x06\x03\x06\x03\x06\x03\x07\x03\x07" +
		"\x03\x07\x03\b\x03\b\x03\b\x03\t\x03\t\x03\t\x03\t\x03\t\x03\t\x03\t\x03" +
		"\t\x03\t\x03\t\x03\t\x03\t\x05\t\xA9\n\t\x03\n\x03\n\x03\n\x03\v\x03\v" +
		"\x03\v\x03\v\x03\v\x03\v\x03\f\x03\f\x03\f\x03\f\x03\f\x03\f\x03\f\x05" +
		"\f\xBB\n\f\x03\r\x03\r\x03\r\x03\r\x03\r\x03\r\x03\x0E\x03\x0E\x03\x0E" +
		"\x03\x0E\x03\x0E\x03\x0E\x03\x0E\x03\x0E\x03\x0F\x03\x0F\x03\x0F\x03\x0F" +
		"\x03\x0F\x05\x0F\xD0\n\x0F\x03\x0F\x05\x0F\xD3\n\x0F\x03\x0F\x03\x0F\x05" +
		"\x0F\xD7\n\x0F\x03\x0F\x03\x0F\x03\x0F\x03\x10\x03\x10\x03\x10\x03\x10" +
		"\x03\x10\x03\x10\x03\x10\x03\x10\x03\x11\x03\x11\x03\x11\x03\x12\x03\x12" +
		"\x03\x12\x03\x13\x03\x13\x05\x13\xEC\n\x13\x03\x13\x03\x13\x03\x14\x03" +
		"\x14\x03\x14\x03\x14\x03\x14\x03\x14\x03\x14\x03\x14\x03\x15\x03\x15\x03" +
		"\x15\x03\x15\x03\x15\x03\x15\x07\x15\xFE\n\x15\f\x15\x0E\x15\u0101\v\x15" +
		"\x03\x15\x05\x15\u0104\n\x15\x03\x15\x03\x15\x03\x16\x03\x16\x03\x16\x03" +
		"\x16\x07\x16\u010C\n\x16\f\x16\x0E\x16\u010F\v\x16\x03\x17\x03\x17\x03" +
		"\x17\x07\x17\u0114\n\x17\f\x17\x0E\x17\u0117\v\x17\x03\x18\x03\x18\x03" +
		"\x18\x03\x18\x05\x18\u011D\n\x18\x03\x18\x03\x18\x03\x18\x05\x18\u0122" +
		"\n\x18\x03\x18\x03\x18\x03\x19\x03\x19\x03\x19\x07\x19\u0129\n\x19\f\x19" +
		"\x0E\x19\u012C\v\x19\x03\x1A\x03\x1A\x03\x1A\x05\x1A\u0131\n\x1A\x03\x1B" +
		"\x03\x1B\x03\x1B\x03\x1B\x05\x1B\u0137\n\x1B\x03\x1B\x03\x1B\x07\x1B\u013B" +
		"\n\x1B\f\x1B\x0E\x1B\u013E\v\x1B\x03\x1B\x03\x1B\x03\x1C\x03\x1C\x03\x1C" +
		"\x05\x1C\u0145\n\x1C\x03\x1D\x03\x1D\x03\x1E\x03\x1E\x03\x1E\x03\x1E\x03" +
		"\x1E\x03\x1E\x03\x1E\x03\x1E\x03\x1E\x03\x1E\x03\x1E\x05\x1E\u0154\n\x1E" +
		"\x03\x1F\x03\x1F\x03\x1F\x03\x1F\x03\x1F\x03\x1F\x05\x1F\u015C\n\x1F\x03" +
		" \x03 \x03 \x07 \u0161\n \f \x0E \u0164\v \x03!\x03!\x03!\x07!\u0169\n" +
		"!\f!\x0E!\u016C\v!\x03\"\x03\"\x03\"\x07\"\u0171\n\"\f\"\x0E\"\u0174\v" +
		"\"\x03#\x03#\x03#\x07#\u0179\n#\f#\x0E#\u017C\v#\x03$\x03$\x03$\x07$\u0181" +
		"\n$\f$\x0E$\u0184\v$\x03%\x03%\x03%\x07%\u0189\n%\f%\x0E%\u018C\v%\x03" +
		"&\x03&\x03&\x05&\u0191\n&\x03\'\x03\'\x03\'\x03\'\x03\'\x03\'\x05\'\u0199" +
		"\n\'\x03(\x03(\x03(\x03(\x03(\x05(\u01A0\n(\x03)\x03)\x07)\u01A4\n)\f" +
		")\x0E)\u01A7\v)\x03*\x03*\x03*\x03*\x03*\x05*\u01AE\n*\x03*\x03*\x05*" +
		"\u01B2\n*\x03+\x03+\x05+\u01B6\n+\x03+\x03+\x03+\x03+\x03+\x03+\x03+\x05" +
		"+\u01BF\n+\x03,\x03,\x03,\x07,\u01C4\n,\f,\x0E,\u01C7\v,\x03-\x03-\x03" +
		"-\x03-\x07-\u01CD\n-\f-\x0E-\u01D0\v-\x05-\u01D2\n-\x03-\x03-\x03.\x03" +
		".\x03.\x07.\u01D9\n.\f.\x0E.\u01DC\v.\x03/\x03/\x03/\x02\x02\x020\x02" +
		"\x02\x04\x02\x06\x02\b\x02\n\x02\f\x02\x0E\x02\x10\x02\x12\x02\x14\x02" +
		"\x16\x02\x18\x02\x1A\x02\x1C\x02\x1E\x02 \x02\"\x02$\x02&\x02(\x02*\x02" +
		",\x02.\x020\x022\x024\x026\x028\x02:\x02<\x02>\x02@\x02B\x02D\x02F\x02" +
		"H\x02J\x02L\x02N\x02P\x02R\x02T\x02V\x02X\x02Z\x02\\\x02\x02\t\x03\x02" +
		"\x05\x06\x03\x02$%\x03\x02&)\x03\x02*+\x03\x02,.\x04\x02++//\x04\x027" +
		"9==\x02\u01F5\x02a\x03\x02\x02\x02\x04x\x03\x02\x02\x02\x06z\x03\x02\x02" +
		"\x02\b\x83\x03\x02\x02\x02\n\x8D\x03\x02\x02\x02\f\x96\x03\x02\x02\x02" +
		"\x0E\x99\x03\x02\x02\x02\x10\xA8\x03\x02\x02\x02\x12\xAA\x03\x02\x02\x02" +
		"\x14\xAD\x03\x02\x02\x02\x16\xB3\x03\x02\x02\x02\x18\xBC\x03\x02\x02\x02" +
		"\x1A\xC2\x03\x02\x02\x02\x1C\xCA\x03\x02\x02\x02\x1E\xDB\x03\x02\x02\x02" +
		" \xE3\x03\x02\x02\x02\"\xE6\x03\x02\x02\x02$\xE9\x03\x02\x02\x02&\xEF" +
		"\x03\x02\x02\x02(\xF7\x03\x02\x02\x02*\u0107\x03\x02\x02\x02,\u0110\x03" +
		"\x02\x02\x02.\u0118\x03\x02\x02\x020\u0125\x03\x02\x02\x022\u012D\x03" +
		"\x02\x02\x024\u0132\x03\x02\x02\x026\u0144\x03\x02\x02\x028\u0146\x03" +
		"\x02\x02\x02:\u0153\x03\x02\x02\x02<\u0155\x03\x02\x02\x02>\u015D\x03" +
		"\x02\x02\x02@\u0165\x03\x02\x02\x02B\u016D\x03\x02\x02\x02D\u0175\x03" +
		"\x02\x02\x02F\u017D\x03\x02\x02\x02H\u0185\x03\x02\x02\x02J\u0190\x03" +
		"\x02\x02\x02L\u0198\x03\x02\x02\x02N\u019F\x03\x02\x02\x02P\u01A1\x03" +
		"\x02\x02\x02R\u01B1\x03\x02\x02\x02T\u01BE\x03\x02\x02\x02V\u01C0\x03" +
		"\x02\x02\x02X\u01C8\x03\x02\x02\x02Z\u01D5\x03\x02\x02\x02\\\u01DD\x03" +
		"\x02\x02\x02^`\x05\x04\x03\x02_^\x03\x02\x02\x02`c\x03\x02\x02\x02a_\x03" +
		"\x02\x02\x02ab\x03\x02\x02\x02bd\x03\x02\x02\x02ca\x03\x02\x02\x02de\x07" +
		"\x02\x02\x03e\x03\x03\x02\x02\x02fy\x05\b\x05\x02gy\x05\n\x06\x02hy\x05" +
		"\x10\t\x02iy\x05.\x18\x02jy\x054\x1B\x02ky\x05\x12\n\x02ly\x05\x14\v\x02" +
		"my\x05\x06\x04\x02ny\x05\x16\f\x02oy\x05\x18\r\x02py\x05\x1A\x0E\x02q" +
		"y\x05\x1C\x0F\x02ry\x05\x1E\x10\x02sy\x05&\x14\x02ty\x05(\x15\x02uy\x05" +
		" \x11\x02vy\x05\"\x12\x02wy\x05$\x13\x02xf\x03\x02\x02\x02xg\x03\x02\x02" +
		"\x02xh\x03\x02\x02\x02xi\x03\x02\x02\x02xj\x03\x02\x02\x02xk\x03\x02\x02" +
		"\x02xl\x03\x02\x02\x02xm\x03\x02\x02\x02xn\x03\x02\x02\x02xo\x03\x02\x02" +
		"\x02xp\x03\x02\x02\x02xq\x03\x02\x02\x02xr\x03\x02\x02\x02xs\x03\x02\x02" +
		"\x02xt\x03\x02\x02\x02xu\x03\x02\x02\x02xv\x03\x02\x02\x02xw\x03\x02\x02" +
		"\x02y\x05\x03\x02\x02\x02z~\x07\x03\x02\x02{}\x05\x04\x03\x02|{\x03\x02" +
		"\x02\x02}\x80\x03\x02\x02\x02~|\x03\x02\x02\x02~\x7F\x03\x02\x02\x02\x7F" +
		"\x81\x03\x02\x02\x02\x80~\x03\x02\x02\x02\x81\x82\x07\x04\x02\x02\x82" +
		"\x07\x03\x02\x02\x02\x83\x84\t\x02\x02\x02\x84\x86\x07=\x02\x02\x85\x87" +
		"\x05\f\x07\x02\x86\x85\x03\x02\x02\x02\x86\x87\x03\x02\x02\x02\x87\x89" +
		"\x03\x02\x02\x02\x88\x8A\x05\x0E\b\x02\x89\x88\x03\x02\x02\x02\x89\x8A" +
		"\x03\x02\x02\x02\x8A\x8B\x03\x02\x02\x02\x8B\x8C\x07\x07\x02\x02\x8C\t" +
		"\x03\x02\x02\x02\x8D\x8E\x07\b\x02\x02\x8E\x90\x07=\x02\x02\x8F\x91\x05" +
		"\f\x07\x02\x90\x8F\x03\x02\x02\x02\x90\x91\x03\x02\x02\x02\x91\x92\x03" +
		"\x02\x02\x02\x92\x93\x07\t\x02\x02\x93\x94\x058\x1D\x02\x94\x95\x07\x07" +
		"\x02\x02\x95\v\x03\x02\x02\x02\x96\x97\x07\n\x02\x02\x97\x98\x05Z.\x02" +
		"\x98\r\x03\x02\x02\x02\x99\x9A\x07\t\x02\x02\x9A\x9B\x058\x1D\x02\x9B" +
		"\x0F\x03\x02\x02\x02\x9C\x9D\x07=\x02\x02\x9D\x9E\x07\t\x02\x02\x9E\x9F" +
		"\x058\x1D\x02\x9F\xA0\x07\x07\x02\x02\xA0\xA9\x03\x02\x02\x02\xA1\xA2" +
		"\x058\x1D\x02\xA2\xA3\x07\v\x02\x02\xA3\xA4\x07=\x02\x02\xA4\xA5\x07\t" +
		"\x02\x02\xA5\xA6\x058\x1D\x02\xA6\xA7\x07\x07\x02\x02\xA7\xA9\x03\x02" +
		"\x02\x02\xA8\x9C\x03\x02\x02\x02\xA8\xA1\x03\x02\x02\x02\xA9\x11\x03\x02" +
		"\x02\x02\xAA\xAB\x058\x1D\x02\xAB\xAC\x07\x07\x02\x02\xAC\x13\x03\x02" +
		"\x02\x02\xAD\xAE\x07\f\x02\x02\xAE\xAF\x07\r\x02\x02\xAF\xB0\x058\x1D" +
		"\x02\xB0\xB1\x07\x0E\x02\x02\xB1\xB2\x07\x07\x02\x02\xB2\x15\x03\x02\x02" +
		"\x02\xB3\xB4\x07\x0F\x02\x02\xB4\xB5\x07\r\x02\x02\xB5\xB6\x058\x1D\x02" +
		"\xB6\xB7\x07\x0E\x02\x02\xB7\xBA\x05\x06\x04\x02\xB8\xB9\x07\x10\x02\x02" +
		"\xB9\xBB\x05\x06\x04\x02\xBA\xB8\x03\x02\x02\x02\xBA\xBB\x03\x02\x02\x02" +
		"\xBB\x17\x03\x02\x02\x02\xBC\xBD\x07\x11\x02\x02\xBD\xBE\x07\r\x02\x02" +
		"\xBE\xBF\x058\x1D\x02\xBF\xC0\x07\x0E\x02\x02\xC0\xC1\x05\x06\x04\x02" +
		"\xC1\x19\x03\x02\x02\x02\xC2\xC3\x07\x12\x02\x02\xC3\xC4\x05\x06\x04\x02" +
		"\xC4\xC5\x07\x11\x02\x02\xC5\xC6\x07\r\x02\x02\xC6\xC7\x058\x1D\x02\xC7" +
		"\xC8\x07\x0E\x02\x02\xC8\xC9\x07\x07\x02\x02\xC9\x1B\x03\x02\x02\x02\xCA" +
		"\xCB\x07\x13\x02\x02\xCB\xCF\x07\r\x02\x02\xCC\xD0\x05\b\x05\x02\xCD\xD0" +
		"\x05\x10\t\x02\xCE\xD0\x07\x07\x02\x02\xCF\xCC\x03\x02\x02\x02\xCF\xCD" +
		"\x03\x02\x02\x02\xCF\xCE\x03\x02\x02\x02\xD0\xD2\x03\x02\x02\x02\xD1\xD3" +
		"\x058\x1D\x02\xD2\xD1\x03\x02\x02\x02\xD2\xD3\x03\x02\x02\x02\xD3\xD4" +
		"\x03\x02\x02\x02\xD4\xD6\x07\x07\x02\x02\xD5\xD7\x058\x1D\x02\xD6\xD5" +
		"\x03\x02\x02\x02\xD6\xD7\x03\x02\x02\x02\xD7\xD8\x03\x02\x02\x02\xD8\xD9" +
		"\x07\x0E\x02\x02\xD9\xDA\x05\x06\x04\x02\xDA\x1D\x03\x02\x02\x02\xDB\xDC" +
		"\x07\x14\x02\x02\xDC\xDD\x07\r\x02\x02\xDD\xDE\x07=\x02\x02\xDE\xDF\x07" +
		"\x15\x02\x02\xDF\xE0\x058\x1D\x02\xE0\xE1\x07\x0E\x02\x02\xE1\xE2\x05" +
		"\x06\x04\x02\xE2\x1F\x03\x02\x02\x02\xE3\xE4\x07\x16\x02\x02\xE4\xE5\x07" +
		"\x07\x02\x02\xE5!\x03\x02\x02\x02\xE6\xE7\x07\x17\x02\x02\xE7\xE8\x07" +
		"\x07\x02\x02\xE8#\x03\x02\x02\x02\xE9\xEB\x07\x18\x02\x02\xEA\xEC\x05" +
		"8\x1D\x02\xEB\xEA\x03\x02\x02\x02\xEB\xEC\x03\x02\x02\x02\xEC\xED\x03" +
		"\x02\x02\x02\xED\xEE\x07\x07\x02\x02\xEE%\x03\x02\x02\x02\xEF\xF0\x07" +
		"\x19\x02\x02\xF0\xF1\x05\x06\x04\x02\xF1\xF2\x07\x1A\x02\x02\xF2\xF3\x07" +
		"\r\x02\x02\xF3\xF4\x07=\x02\x02\xF4\xF5\x07\x0E\x02\x02\xF5\xF6\x05\x06" +
		"\x04\x02\xF6\'\x03\x02\x02\x02\xF7\xF8\x07\x1B\x02\x02\xF8\xF9\x07\r\x02" +
		"\x02\xF9\xFA\x058\x1D\x02\xFA\xFB\x07\x0E\x02\x02\xFB\xFF\x07\x03\x02" +
		"\x02\xFC\xFE\x05*\x16\x02\xFD\xFC\x03\x02\x02\x02\xFE\u0101\x03\x02\x02" +
		"\x02\xFF\xFD\x03\x02\x02\x02\xFF\u0100\x03\x02\x02\x02\u0100\u0103\x03" +
		"\x02\x02\x02\u0101\xFF\x03\x02\x02\x02\u0102\u0104\x05,\x17\x02\u0103" +
		"\u0102\x03\x02\x02\x02\u0103\u0104\x03\x02\x02\x02\u0104\u0105\x03\x02" +
		"\x02\x02\u0105\u0106\x07\x04\x02\x02\u0106)\x03\x02\x02\x02\u0107\u0108" +
		"\x07\x1C\x02\x02\u0108\u0109\x058\x1D\x02\u0109\u010D\x07\n\x02\x02\u010A" +
		"\u010C\x05\x04\x03\x02\u010B\u010A\x03\x02\x02\x02\u010C\u010F\x03\x02" +
		"\x02\x02\u010D\u010B\x03\x02\x02\x02\u010D\u010E\x03\x02\x02\x02\u010E" +
		"+\x03\x02\x02\x02\u010F\u010D\x03\x02\x02\x02\u0110\u0111\x07\x1D\x02" +
		"\x02\u0111\u0115\x07\n\x02\x02\u0112\u0114\x05\x04\x03\x02\u0113\u0112" +
		"\x03\x02\x02\x02\u0114\u0117\x03\x02\x02\x02\u0115\u0113\x03\x02\x02\x02" +
		"\u0115\u0116\x03\x02\x02\x02\u0116-\x03\x02\x02\x02\u0117\u0115\x03\x02" +
		"\x02\x02\u0118\u0119\x07\x1E\x02\x02\u0119\u011A\x07=\x02\x02\u011A\u011C" +
		"\x07\r\x02\x02\u011B\u011D\x050\x19\x02\u011C\u011B\x03\x02\x02\x02\u011C" +
		"\u011D\x03\x02\x02\x02\u011D\u011E\x03\x02\x02\x02\u011E\u0121\x07\x0E" +
		"\x02\x02\u011F\u0120\x07\n\x02\x02\u0120\u0122\x05Z.\x02\u0121\u011F\x03" +
		"\x02\x02\x02\u0121\u0122\x03\x02\x02\x02\u0122\u0123\x03\x02\x02\x02\u0123" +
		"\u0124\x05\x06\x04\x02\u0124/\x03\x02\x02\x02\u0125\u012A\x052\x1A\x02" +
		"\u0126\u0127\x07\x1F\x02\x02\u0127\u0129\x052\x1A\x02\u0128\u0126\x03" +
		"\x02\x02\x02\u0129\u012C\x03\x02\x02\x02\u012A\u0128\x03\x02\x02\x02\u012A" +
		"\u012B\x03\x02\x02\x02\u012B1\x03\x02\x02\x02\u012C\u012A\x03\x02\x02" +
		"\x02\u012D\u0130\x07=\x02\x02\u012E\u012F\x07\n\x02\x02\u012F\u0131\x05" +
		"Z.\x02\u0130\u012E\x03\x02\x02\x02\u0130\u0131\x03\x02\x02\x02\u01313" +
		"\x03\x02\x02\x02\u0132\u0133\x07 \x02\x02\u0133\u0136\x07=\x02\x02\u0134" +
		"\u0135\x07\n\x02\x02\u0135\u0137\x07=\x02\x02\u0136\u0134\x03\x02\x02" +
		"\x02\u0136\u0137\x03\x02\x02\x02\u0137\u0138\x03\x02\x02\x02\u0138\u013C" +
		"\x07\x03\x02\x02\u0139\u013B\x056\x1C\x02\u013A\u0139\x03\x02\x02\x02" +
		"\u013B\u013E\x03\x02\x02\x02\u013C\u013A\x03\x02\x02\x02\u013C\u013D\x03" +
		"\x02\x02\x02\u013D\u013F\x03\x02\x02\x02\u013E\u013C\x03\x02\x02\x02\u013F" +
		"\u0140\x07\x04\x02\x02\u01405\x03\x02\x02\x02\u0141\u0145\x05.\x18\x02" +
		"\u0142\u0145\x05\b\x05\x02\u0143\u0145\x05\n\x06\x02\u0144\u0141\x03\x02" +
		"\x02\x02\u0144\u0142\x03\x02\x02\x02\u0144\u0143\x03\x02\x02\x02\u0145" +
		"7\x03\x02\x02\x02\u0146\u0147\x05:\x1E\x02\u01479\x03\x02\x02\x02\u0148" +
		"\u0149\x05P)\x02\u0149\u014A\x07\t\x02\x02\u014A\u014B\x05:\x1E\x02\u014B" +
		"\u0154\x03\x02\x02\x02\u014C\u014D\x05P)\x02\u014D\u014E\x07\v\x02\x02" +
		"\u014E\u014F\x07=\x02\x02\u014F\u0150\x07\t\x02\x02\u0150\u0151\x05:\x1E" +
		"\x02\u0151\u0154\x03\x02\x02\x02\u0152\u0154\x05<\x1F\x02\u0153\u0148" +
		"\x03\x02\x02\x02\u0153\u014C\x03\x02\x02\x02\u0153\u0152\x03\x02\x02\x02" +
		"\u0154;\x03\x02\x02\x02\u0155\u015B\x05> \x02\u0156\u0157\x07!\x02\x02" +
		"\u0157\u0158\x058\x1D\x02\u0158\u0159\x07\n\x02\x02\u0159\u015A\x058\x1D" +
		"\x02\u015A\u015C\x03\x02\x02\x02\u015B\u0156\x03\x02\x02\x02\u015B\u015C" +
		"\x03\x02\x02\x02\u015C=\x03\x02\x02\x02\u015D\u0162\x05@!\x02\u015E\u015F" +
		"\x07\"\x02\x02\u015F\u0161\x05@!\x02\u0160\u015E\x03\x02\x02\x02\u0161" +
		"\u0164\x03\x02\x02\x02\u0162\u0160\x03\x02\x02\x02\u0162\u0163\x03\x02" +
		"\x02\x02\u0163?\x03\x02\x02\x02\u0164\u0162\x03\x02\x02\x02\u0165\u016A" +
		"\x05B\"\x02\u0166\u0167\x07#\x02\x02\u0167\u0169\x05B\"\x02\u0168\u0166" +
		"\x03\x02\x02\x02\u0169\u016C\x03\x02\x02\x02\u016A\u0168\x03\x02\x02\x02" +
		"\u016A\u016B\x03\x02\x02\x02\u016BA\x03\x02\x02\x02\u016C\u016A\x03\x02" +
		"\x02\x02\u016D\u0172\x05D#\x02\u016E\u016F\t\x03\x02\x02\u016F\u0171\x05" +
		"D#\x02\u0170\u016E\x03\x02\x02\x02\u0171\u0174\x03\x02\x02\x02\u0172\u0170" +
		"\x03\x02\x02\x02\u0172\u0173\x03\x02\x02\x02\u0173C\x03\x02\x02\x02\u0174" +
		"\u0172\x03\x02\x02\x02\u0175\u017A\x05F$\x02\u0176\u0177\t\x04\x02\x02" +
		"\u0177\u0179\x05F$\x02\u0178\u0176\x03\x02\x02\x02\u0179\u017C\x03\x02" +
		"\x02\x02\u017A\u0178\x03\x02\x02\x02\u017A\u017B\x03\x02\x02\x02\u017B" +
		"E\x03\x02\x02\x02\u017C\u017A\x03\x02\x02\x02\u017D\u0182\x05H%\x02\u017E" +
		"\u017F\t\x05\x02\x02\u017F\u0181\x05H%\x02\u0180\u017E\x03\x02\x02\x02" +
		"\u0181\u0184\x03\x02\x02\x02\u0182\u0180\x03\x02\x02\x02\u0182\u0183\x03" +
		"\x02\x02\x02\u0183G\x03\x02\x02\x02\u0184\u0182\x03\x02\x02\x02\u0185" +
		"\u018A\x05J&\x02\u0186\u0187\t\x06\x02\x02\u0187\u0189\x05J&\x02\u0188" +
		"\u0186\x03\x02\x02\x02\u0189\u018C\x03\x02\x02\x02\u018A\u0188\x03\x02" +
		"\x02\x02\u018A\u018B\x03\x02\x02\x02\u018BI\x03\x02\x02\x02\u018C\u018A" +
		"\x03\x02\x02\x02\u018D\u018E\t\x07\x02\x02\u018E\u0191\x05J&\x02\u018F" +
		"\u0191\x05L\'\x02\u0190\u018D\x03\x02\x02\x02\u0190\u018F\x03\x02\x02" +
		"\x02\u0191K\x03\x02\x02\x02\u0192\u0199\x05N(\x02\u0193\u0199\x05P)\x02" +
		"\u0194\u0195\x07\r\x02\x02\u0195\u0196\x058\x1D\x02\u0196\u0197\x07\x0E" +
		"\x02\x02\u0197\u0199\x03\x02\x02\x02\u0198\u0192\x03\x02\x02\x02\u0198" +
		"\u0193\x03\x02\x02\x02\u0198\u0194\x03\x02\x02\x02\u0199M\x03\x02\x02" +
		"\x02\u019A\u01A0\x07:\x02\x02\u019B\u01A0\x05X-\x02\u019C\u01A0\x070\x02" +
		"\x02\u019D\u01A0\x071\x02\x02\u019E\u01A0\x072\x02\x02\u019F\u019A\x03" +
		"\x02\x02\x02\u019F\u019B\x03\x02\x02\x02\u019F\u019C\x03\x02\x02\x02\u019F" +
		"\u019D\x03\x02\x02\x02\u019F\u019E\x03\x02\x02\x02\u01A0O\x03\x02\x02" +
		"\x02\u01A1\u01A5\x05R*\x02\u01A2\u01A4\x05T+\x02\u01A3\u01A2\x03\x02\x02" +
		"\x02\u01A4\u01A7\x03\x02\x02\x02\u01A5\u01A3\x03\x02\x02\x02\u01A5\u01A6" +
		"\x03\x02\x02\x02\u01A6Q\x03\x02\x02\x02\u01A7\u01A5\x03\x02\x02\x02\u01A8" +
		"\u01B2\x07=\x02\x02\u01A9\u01AA\x073\x02\x02\u01AA\u01AB\x07=\x02\x02" +
		"\u01AB\u01AD\x07\r\x02\x02\u01AC\u01AE\x05V,\x02\u01AD\u01AC\x03\x02\x02" +
		"\x02\u01AD\u01AE\x03\x02\x02\x02\u01AE\u01AF\x03\x02\x02\x02\u01AF\u01B2" +
		"\x07\x0E\x02\x02\u01B0\u01B2\x074\x02\x02\u01B1\u01A8\x03\x02\x02\x02" +
		"\u01B1\u01A9\x03\x02\x02\x02\u01B1\u01B0\x03\x02\x02\x02\u01B2S\x03\x02" +
		"\x02\x02\u01B3\u01B5\x07\r\x02\x02\u01B4\u01B6\x05V,\x02\u01B5\u01B4\x03" +
		"\x02\x02\x02\u01B5\u01B6\x03\x02\x02\x02\u01B6\u01B7\x03\x02\x02\x02\u01B7" +
		"\u01BF\x07\x0E\x02\x02\u01B8\u01B9\x075\x02\x02\u01B9\u01BA\x058\x1D\x02" +
		"\u01BA\u01BB\x076\x02\x02\u01BB\u01BF\x03\x02\x02\x02\u01BC\u01BD\x07" +
		"\v\x02\x02\u01BD\u01BF\x07=\x02\x02\u01BE\u01B3\x03\x02\x02\x02\u01BE" +
		"\u01B8\x03\x02\x02\x02\u01BE\u01BC\x03\x02\x02\x02\u01BFU\x03\x02\x02" +
		"\x02\u01C0\u01C5\x058\x1D\x02\u01C1\u01C2\x07\x1F\x02\x02\u01C2\u01C4" +
		"\x058\x1D\x02\u01C3\u01C1\x03\x02\x02\x02\u01C4\u01C7\x03\x02\x02\x02" +
		"\u01C5\u01C3\x03\x02\x02\x02\u01C5\u01C6\x03\x02\x02\x02\u01C6W\x03\x02" +
		"\x02\x02\u01C7\u01C5\x03\x02\x02\x02\u01C8\u01D1\x075\x02\x02\u01C9\u01CE" +
		"\x058\x1D\x02\u01CA\u01CB\x07\x1F\x02\x02\u01CB\u01CD\x058\x1D\x02\u01CC" +
		"\u01CA\x03\x02\x02\x02\u01CD\u01D0\x03\x02\x02\x02\u01CE\u01CC\x03\x02" +
		"\x02\x02\u01CE\u01CF\x03\x02\x02\x02\u01CF\u01D2\x03\x02\x02\x02\u01D0" +
		"\u01CE\x03\x02\x02\x02\u01D1\u01C9\x03\x02\x02\x02\u01D1\u01D2\x03\x02" +
		"\x02\x02\u01D2\u01D3\x03\x02\x02\x02\u01D3\u01D4\x076\x02\x02\u01D4Y\x03" +
		"\x02\x02\x02\u01D5\u01DA\x05\\/\x02\u01D6\u01D7\x075\x02\x02\u01D7\u01D9" +
		"\x076\x02\x02\u01D8\u01D6\x03\x02\x02\x02\u01D9\u01DC\x03\x02\x02\x02" +
		"\u01DA\u01D8\x03\x02\x02\x02\u01DA\u01DB\x03\x02\x02\x02\u01DB[\x03\x02" +
		"\x02\x02\u01DC\u01DA\x03\x02\x02\x02\u01DD\u01DE\t\b\x02\x02\u01DE]\x03" +
		"\x02\x02\x02-ax~\x86\x89\x90\xA8\xBA\xCF\xD2\xD6\xEB\xFF\u0103\u010D\u0115" +
		"\u011C\u0121\u012A\u0130\u0136\u013C\u0144\u0153\u015B\u0162\u016A\u0172" +
		"\u017A\u0182\u018A\u0190\u0198\u019F\u01A5\u01AD\u01B1\u01B5\u01BE\u01C5" +
		"\u01CE\u01D1\u01DA";
	public static __ATN: ATN;
	public static get _ATN(): ATN {
		if (!CompiscriptParser.__ATN) {
			CompiscriptParser.__ATN = new ATNDeserializer().deserialize(Utils.toCharArray(CompiscriptParser._serializedATN));
		}

		return CompiscriptParser.__ATN;
	}

}

export class ProgramContext extends ParserRuleContext {
	public EOF(): TerminalNode { return this.getToken(CompiscriptParser.EOF, 0); }
	public statement(): StatementContext[];
	public statement(i: number): StatementContext;
	public statement(i?: number): StatementContext | StatementContext[] {
		if (i === undefined) {
			return this.getRuleContexts(StatementContext);
		} else {
			return this.getRuleContext(i, StatementContext);
		}
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_program; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterProgram) {
			listener.enterProgram(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitProgram) {
			listener.exitProgram(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitProgram) {
			return visitor.visitProgram(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class StatementContext extends ParserRuleContext {
	public variableDeclaration(): VariableDeclarationContext | undefined {
		return this.tryGetRuleContext(0, VariableDeclarationContext);
	}
	public constantDeclaration(): ConstantDeclarationContext | undefined {
		return this.tryGetRuleContext(0, ConstantDeclarationContext);
	}
	public assignment(): AssignmentContext | undefined {
		return this.tryGetRuleContext(0, AssignmentContext);
	}
	public functionDeclaration(): FunctionDeclarationContext | undefined {
		return this.tryGetRuleContext(0, FunctionDeclarationContext);
	}
	public classDeclaration(): ClassDeclarationContext | undefined {
		return this.tryGetRuleContext(0, ClassDeclarationContext);
	}
	public expressionStatement(): ExpressionStatementContext | undefined {
		return this.tryGetRuleContext(0, ExpressionStatementContext);
	}
	public printStatement(): PrintStatementContext | undefined {
		return this.tryGetRuleContext(0, PrintStatementContext);
	}
	public block(): BlockContext | undefined {
		return this.tryGetRuleContext(0, BlockContext);
	}
	public ifStatement(): IfStatementContext | undefined {
		return this.tryGetRuleContext(0, IfStatementContext);
	}
	public whileStatement(): WhileStatementContext | undefined {
		return this.tryGetRuleContext(0, WhileStatementContext);
	}
	public doWhileStatement(): DoWhileStatementContext | undefined {
		return this.tryGetRuleContext(0, DoWhileStatementContext);
	}
	public forStatement(): ForStatementContext | undefined {
		return this.tryGetRuleContext(0, ForStatementContext);
	}
	public foreachStatement(): ForeachStatementContext | undefined {
		return this.tryGetRuleContext(0, ForeachStatementContext);
	}
	public tryCatchStatement(): TryCatchStatementContext | undefined {
		return this.tryGetRuleContext(0, TryCatchStatementContext);
	}
	public switchStatement(): SwitchStatementContext | undefined {
		return this.tryGetRuleContext(0, SwitchStatementContext);
	}
	public breakStatement(): BreakStatementContext | undefined {
		return this.tryGetRuleContext(0, BreakStatementContext);
	}
	public continueStatement(): ContinueStatementContext | undefined {
		return this.tryGetRuleContext(0, ContinueStatementContext);
	}
	public returnStatement(): ReturnStatementContext | undefined {
		return this.tryGetRuleContext(0, ReturnStatementContext);
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_statement; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterStatement) {
			listener.enterStatement(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitStatement) {
			listener.exitStatement(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitStatement) {
			return visitor.visitStatement(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class BlockContext extends ParserRuleContext {
	public statement(): StatementContext[];
	public statement(i: number): StatementContext;
	public statement(i?: number): StatementContext | StatementContext[] {
		if (i === undefined) {
			return this.getRuleContexts(StatementContext);
		} else {
			return this.getRuleContext(i, StatementContext);
		}
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_block; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterBlock) {
			listener.enterBlock(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitBlock) {
			listener.exitBlock(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitBlock) {
			return visitor.visitBlock(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class VariableDeclarationContext extends ParserRuleContext {
	public Identifier(): TerminalNode { return this.getToken(CompiscriptParser.Identifier, 0); }
	public typeAnnotation(): TypeAnnotationContext | undefined {
		return this.tryGetRuleContext(0, TypeAnnotationContext);
	}
	public initializer(): InitializerContext | undefined {
		return this.tryGetRuleContext(0, InitializerContext);
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_variableDeclaration; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterVariableDeclaration) {
			listener.enterVariableDeclaration(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitVariableDeclaration) {
			listener.exitVariableDeclaration(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitVariableDeclaration) {
			return visitor.visitVariableDeclaration(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class ConstantDeclarationContext extends ParserRuleContext {
	public Identifier(): TerminalNode { return this.getToken(CompiscriptParser.Identifier, 0); }
	public expression(): ExpressionContext {
		return this.getRuleContext(0, ExpressionContext);
	}
	public typeAnnotation(): TypeAnnotationContext | undefined {
		return this.tryGetRuleContext(0, TypeAnnotationContext);
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_constantDeclaration; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterConstantDeclaration) {
			listener.enterConstantDeclaration(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitConstantDeclaration) {
			listener.exitConstantDeclaration(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitConstantDeclaration) {
			return visitor.visitConstantDeclaration(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class TypeAnnotationContext extends ParserRuleContext {
	public type(): TypeContext {
		return this.getRuleContext(0, TypeContext);
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_typeAnnotation; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterTypeAnnotation) {
			listener.enterTypeAnnotation(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitTypeAnnotation) {
			listener.exitTypeAnnotation(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitTypeAnnotation) {
			return visitor.visitTypeAnnotation(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class InitializerContext extends ParserRuleContext {
	public expression(): ExpressionContext {
		return this.getRuleContext(0, ExpressionContext);
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_initializer; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterInitializer) {
			listener.enterInitializer(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitInitializer) {
			listener.exitInitializer(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitInitializer) {
			return visitor.visitInitializer(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class AssignmentContext extends ParserRuleContext {
	public Identifier(): TerminalNode { return this.getToken(CompiscriptParser.Identifier, 0); }
	public expression(): ExpressionContext[];
	public expression(i: number): ExpressionContext;
	public expression(i?: number): ExpressionContext | ExpressionContext[] {
		if (i === undefined) {
			return this.getRuleContexts(ExpressionContext);
		} else {
			return this.getRuleContext(i, ExpressionContext);
		}
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_assignment; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterAssignment) {
			listener.enterAssignment(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitAssignment) {
			listener.exitAssignment(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitAssignment) {
			return visitor.visitAssignment(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class ExpressionStatementContext extends ParserRuleContext {
	public expression(): ExpressionContext {
		return this.getRuleContext(0, ExpressionContext);
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_expressionStatement; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterExpressionStatement) {
			listener.enterExpressionStatement(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitExpressionStatement) {
			listener.exitExpressionStatement(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitExpressionStatement) {
			return visitor.visitExpressionStatement(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class PrintStatementContext extends ParserRuleContext {
	public expression(): ExpressionContext {
		return this.getRuleContext(0, ExpressionContext);
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_printStatement; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterPrintStatement) {
			listener.enterPrintStatement(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitPrintStatement) {
			listener.exitPrintStatement(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitPrintStatement) {
			return visitor.visitPrintStatement(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class IfStatementContext extends ParserRuleContext {
	public expression(): ExpressionContext {
		return this.getRuleContext(0, ExpressionContext);
	}
	public block(): BlockContext[];
	public block(i: number): BlockContext;
	public block(i?: number): BlockContext | BlockContext[] {
		if (i === undefined) {
			return this.getRuleContexts(BlockContext);
		} else {
			return this.getRuleContext(i, BlockContext);
		}
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_ifStatement; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterIfStatement) {
			listener.enterIfStatement(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitIfStatement) {
			listener.exitIfStatement(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitIfStatement) {
			return visitor.visitIfStatement(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class WhileStatementContext extends ParserRuleContext {
	public expression(): ExpressionContext {
		return this.getRuleContext(0, ExpressionContext);
	}
	public block(): BlockContext {
		return this.getRuleContext(0, BlockContext);
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_whileStatement; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterWhileStatement) {
			listener.enterWhileStatement(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitWhileStatement) {
			listener.exitWhileStatement(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitWhileStatement) {
			return visitor.visitWhileStatement(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class DoWhileStatementContext extends ParserRuleContext {
	public block(): BlockContext {
		return this.getRuleContext(0, BlockContext);
	}
	public expression(): ExpressionContext {
		return this.getRuleContext(0, ExpressionContext);
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_doWhileStatement; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterDoWhileStatement) {
			listener.enterDoWhileStatement(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitDoWhileStatement) {
			listener.exitDoWhileStatement(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitDoWhileStatement) {
			return visitor.visitDoWhileStatement(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class ForStatementContext extends ParserRuleContext {
	public block(): BlockContext {
		return this.getRuleContext(0, BlockContext);
	}
	public variableDeclaration(): VariableDeclarationContext | undefined {
		return this.tryGetRuleContext(0, VariableDeclarationContext);
	}
	public assignment(): AssignmentContext | undefined {
		return this.tryGetRuleContext(0, AssignmentContext);
	}
	public expression(): ExpressionContext[];
	public expression(i: number): ExpressionContext;
	public expression(i?: number): ExpressionContext | ExpressionContext[] {
		if (i === undefined) {
			return this.getRuleContexts(ExpressionContext);
		} else {
			return this.getRuleContext(i, ExpressionContext);
		}
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_forStatement; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterForStatement) {
			listener.enterForStatement(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitForStatement) {
			listener.exitForStatement(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitForStatement) {
			return visitor.visitForStatement(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class ForeachStatementContext extends ParserRuleContext {
	public Identifier(): TerminalNode { return this.getToken(CompiscriptParser.Identifier, 0); }
	public expression(): ExpressionContext {
		return this.getRuleContext(0, ExpressionContext);
	}
	public block(): BlockContext {
		return this.getRuleContext(0, BlockContext);
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_foreachStatement; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterForeachStatement) {
			listener.enterForeachStatement(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitForeachStatement) {
			listener.exitForeachStatement(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitForeachStatement) {
			return visitor.visitForeachStatement(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class BreakStatementContext extends ParserRuleContext {
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_breakStatement; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterBreakStatement) {
			listener.enterBreakStatement(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitBreakStatement) {
			listener.exitBreakStatement(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitBreakStatement) {
			return visitor.visitBreakStatement(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class ContinueStatementContext extends ParserRuleContext {
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_continueStatement; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterContinueStatement) {
			listener.enterContinueStatement(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitContinueStatement) {
			listener.exitContinueStatement(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitContinueStatement) {
			return visitor.visitContinueStatement(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class ReturnStatementContext extends ParserRuleContext {
	public expression(): ExpressionContext | undefined {
		return this.tryGetRuleContext(0, ExpressionContext);
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_returnStatement; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterReturnStatement) {
			listener.enterReturnStatement(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitReturnStatement) {
			listener.exitReturnStatement(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitReturnStatement) {
			return visitor.visitReturnStatement(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class TryCatchStatementContext extends ParserRuleContext {
	public block(): BlockContext[];
	public block(i: number): BlockContext;
	public block(i?: number): BlockContext | BlockContext[] {
		if (i === undefined) {
			return this.getRuleContexts(BlockContext);
		} else {
			return this.getRuleContext(i, BlockContext);
		}
	}
	public Identifier(): TerminalNode { return this.getToken(CompiscriptParser.Identifier, 0); }
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_tryCatchStatement; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterTryCatchStatement) {
			listener.enterTryCatchStatement(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitTryCatchStatement) {
			listener.exitTryCatchStatement(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitTryCatchStatement) {
			return visitor.visitTryCatchStatement(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class SwitchStatementContext extends ParserRuleContext {
	public expression(): ExpressionContext {
		return this.getRuleContext(0, ExpressionContext);
	}
	public switchCase(): SwitchCaseContext[];
	public switchCase(i: number): SwitchCaseContext;
	public switchCase(i?: number): SwitchCaseContext | SwitchCaseContext[] {
		if (i === undefined) {
			return this.getRuleContexts(SwitchCaseContext);
		} else {
			return this.getRuleContext(i, SwitchCaseContext);
		}
	}
	public defaultCase(): DefaultCaseContext | undefined {
		return this.tryGetRuleContext(0, DefaultCaseContext);
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_switchStatement; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterSwitchStatement) {
			listener.enterSwitchStatement(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitSwitchStatement) {
			listener.exitSwitchStatement(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitSwitchStatement) {
			return visitor.visitSwitchStatement(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class SwitchCaseContext extends ParserRuleContext {
	public expression(): ExpressionContext {
		return this.getRuleContext(0, ExpressionContext);
	}
	public statement(): StatementContext[];
	public statement(i: number): StatementContext;
	public statement(i?: number): StatementContext | StatementContext[] {
		if (i === undefined) {
			return this.getRuleContexts(StatementContext);
		} else {
			return this.getRuleContext(i, StatementContext);
		}
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_switchCase; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterSwitchCase) {
			listener.enterSwitchCase(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitSwitchCase) {
			listener.exitSwitchCase(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitSwitchCase) {
			return visitor.visitSwitchCase(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class DefaultCaseContext extends ParserRuleContext {
	public statement(): StatementContext[];
	public statement(i: number): StatementContext;
	public statement(i?: number): StatementContext | StatementContext[] {
		if (i === undefined) {
			return this.getRuleContexts(StatementContext);
		} else {
			return this.getRuleContext(i, StatementContext);
		}
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_defaultCase; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterDefaultCase) {
			listener.enterDefaultCase(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitDefaultCase) {
			listener.exitDefaultCase(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitDefaultCase) {
			return visitor.visitDefaultCase(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class FunctionDeclarationContext extends ParserRuleContext {
	public Identifier(): TerminalNode { return this.getToken(CompiscriptParser.Identifier, 0); }
	public block(): BlockContext {
		return this.getRuleContext(0, BlockContext);
	}
	public parameters(): ParametersContext | undefined {
		return this.tryGetRuleContext(0, ParametersContext);
	}
	public type(): TypeContext | undefined {
		return this.tryGetRuleContext(0, TypeContext);
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_functionDeclaration; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterFunctionDeclaration) {
			listener.enterFunctionDeclaration(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitFunctionDeclaration) {
			listener.exitFunctionDeclaration(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitFunctionDeclaration) {
			return visitor.visitFunctionDeclaration(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class ParametersContext extends ParserRuleContext {
	public parameter(): ParameterContext[];
	public parameter(i: number): ParameterContext;
	public parameter(i?: number): ParameterContext | ParameterContext[] {
		if (i === undefined) {
			return this.getRuleContexts(ParameterContext);
		} else {
			return this.getRuleContext(i, ParameterContext);
		}
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_parameters; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterParameters) {
			listener.enterParameters(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitParameters) {
			listener.exitParameters(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitParameters) {
			return visitor.visitParameters(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class ParameterContext extends ParserRuleContext {
	public Identifier(): TerminalNode { return this.getToken(CompiscriptParser.Identifier, 0); }
	public type(): TypeContext | undefined {
		return this.tryGetRuleContext(0, TypeContext);
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_parameter; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterParameter) {
			listener.enterParameter(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitParameter) {
			listener.exitParameter(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitParameter) {
			return visitor.visitParameter(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class ClassDeclarationContext extends ParserRuleContext {
	public Identifier(): TerminalNode[];
	public Identifier(i: number): TerminalNode;
	public Identifier(i?: number): TerminalNode | TerminalNode[] {
		if (i === undefined) {
			return this.getTokens(CompiscriptParser.Identifier);
		} else {
			return this.getToken(CompiscriptParser.Identifier, i);
		}
	}
	public classMember(): ClassMemberContext[];
	public classMember(i: number): ClassMemberContext;
	public classMember(i?: number): ClassMemberContext | ClassMemberContext[] {
		if (i === undefined) {
			return this.getRuleContexts(ClassMemberContext);
		} else {
			return this.getRuleContext(i, ClassMemberContext);
		}
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_classDeclaration; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterClassDeclaration) {
			listener.enterClassDeclaration(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitClassDeclaration) {
			listener.exitClassDeclaration(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitClassDeclaration) {
			return visitor.visitClassDeclaration(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class ClassMemberContext extends ParserRuleContext {
	public functionDeclaration(): FunctionDeclarationContext | undefined {
		return this.tryGetRuleContext(0, FunctionDeclarationContext);
	}
	public variableDeclaration(): VariableDeclarationContext | undefined {
		return this.tryGetRuleContext(0, VariableDeclarationContext);
	}
	public constantDeclaration(): ConstantDeclarationContext | undefined {
		return this.tryGetRuleContext(0, ConstantDeclarationContext);
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_classMember; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterClassMember) {
			listener.enterClassMember(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitClassMember) {
			listener.exitClassMember(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitClassMember) {
			return visitor.visitClassMember(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class ExpressionContext extends ParserRuleContext {
	public assignmentExpr(): AssignmentExprContext {
		return this.getRuleContext(0, AssignmentExprContext);
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_expression; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterExpression) {
			listener.enterExpression(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitExpression) {
			listener.exitExpression(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitExpression) {
			return visitor.visitExpression(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class AssignmentExprContext extends ParserRuleContext {
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_assignmentExpr; }
	public copyFrom(ctx: AssignmentExprContext): void {
		super.copyFrom(ctx);
	}
}
export class AssignExprContext extends AssignmentExprContext {
	public _lhs!: LeftHandSideContext;
	public assignmentExpr(): AssignmentExprContext {
		return this.getRuleContext(0, AssignmentExprContext);
	}
	public leftHandSide(): LeftHandSideContext {
		return this.getRuleContext(0, LeftHandSideContext);
	}
	constructor(ctx: AssignmentExprContext) {
		super(ctx.parent, ctx.invokingState);
		this.copyFrom(ctx);
	}
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterAssignExpr) {
			listener.enterAssignExpr(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitAssignExpr) {
			listener.exitAssignExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitAssignExpr) {
			return visitor.visitAssignExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}
export class PropertyAssignExprContext extends AssignmentExprContext {
	public _lhs!: LeftHandSideContext;
	public Identifier(): TerminalNode { return this.getToken(CompiscriptParser.Identifier, 0); }
	public assignmentExpr(): AssignmentExprContext {
		return this.getRuleContext(0, AssignmentExprContext);
	}
	public leftHandSide(): LeftHandSideContext {
		return this.getRuleContext(0, LeftHandSideContext);
	}
	constructor(ctx: AssignmentExprContext) {
		super(ctx.parent, ctx.invokingState);
		this.copyFrom(ctx);
	}
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterPropertyAssignExpr) {
			listener.enterPropertyAssignExpr(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitPropertyAssignExpr) {
			listener.exitPropertyAssignExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitPropertyAssignExpr) {
			return visitor.visitPropertyAssignExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}
export class ExprNoAssignContext extends AssignmentExprContext {
	public conditionalExpr(): ConditionalExprContext {
		return this.getRuleContext(0, ConditionalExprContext);
	}
	constructor(ctx: AssignmentExprContext) {
		super(ctx.parent, ctx.invokingState);
		this.copyFrom(ctx);
	}
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterExprNoAssign) {
			listener.enterExprNoAssign(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitExprNoAssign) {
			listener.exitExprNoAssign(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitExprNoAssign) {
			return visitor.visitExprNoAssign(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class ConditionalExprContext extends ParserRuleContext {
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_conditionalExpr; }
	public copyFrom(ctx: ConditionalExprContext): void {
		super.copyFrom(ctx);
	}
}
export class TernaryExprContext extends ConditionalExprContext {
	public logicalOrExpr(): LogicalOrExprContext {
		return this.getRuleContext(0, LogicalOrExprContext);
	}
	public expression(): ExpressionContext[];
	public expression(i: number): ExpressionContext;
	public expression(i?: number): ExpressionContext | ExpressionContext[] {
		if (i === undefined) {
			return this.getRuleContexts(ExpressionContext);
		} else {
			return this.getRuleContext(i, ExpressionContext);
		}
	}
	constructor(ctx: ConditionalExprContext) {
		super(ctx.parent, ctx.invokingState);
		this.copyFrom(ctx);
	}
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterTernaryExpr) {
			listener.enterTernaryExpr(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitTernaryExpr) {
			listener.exitTernaryExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitTernaryExpr) {
			return visitor.visitTernaryExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class LogicalOrExprContext extends ParserRuleContext {
	public logicalAndExpr(): LogicalAndExprContext[];
	public logicalAndExpr(i: number): LogicalAndExprContext;
	public logicalAndExpr(i?: number): LogicalAndExprContext | LogicalAndExprContext[] {
		if (i === undefined) {
			return this.getRuleContexts(LogicalAndExprContext);
		} else {
			return this.getRuleContext(i, LogicalAndExprContext);
		}
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_logicalOrExpr; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterLogicalOrExpr) {
			listener.enterLogicalOrExpr(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitLogicalOrExpr) {
			listener.exitLogicalOrExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitLogicalOrExpr) {
			return visitor.visitLogicalOrExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class LogicalAndExprContext extends ParserRuleContext {
	public equalityExpr(): EqualityExprContext[];
	public equalityExpr(i: number): EqualityExprContext;
	public equalityExpr(i?: number): EqualityExprContext | EqualityExprContext[] {
		if (i === undefined) {
			return this.getRuleContexts(EqualityExprContext);
		} else {
			return this.getRuleContext(i, EqualityExprContext);
		}
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_logicalAndExpr; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterLogicalAndExpr) {
			listener.enterLogicalAndExpr(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitLogicalAndExpr) {
			listener.exitLogicalAndExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitLogicalAndExpr) {
			return visitor.visitLogicalAndExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class EqualityExprContext extends ParserRuleContext {
	public relationalExpr(): RelationalExprContext[];
	public relationalExpr(i: number): RelationalExprContext;
	public relationalExpr(i?: number): RelationalExprContext | RelationalExprContext[] {
		if (i === undefined) {
			return this.getRuleContexts(RelationalExprContext);
		} else {
			return this.getRuleContext(i, RelationalExprContext);
		}
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_equalityExpr; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterEqualityExpr) {
			listener.enterEqualityExpr(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitEqualityExpr) {
			listener.exitEqualityExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitEqualityExpr) {
			return visitor.visitEqualityExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class RelationalExprContext extends ParserRuleContext {
	public additiveExpr(): AdditiveExprContext[];
	public additiveExpr(i: number): AdditiveExprContext;
	public additiveExpr(i?: number): AdditiveExprContext | AdditiveExprContext[] {
		if (i === undefined) {
			return this.getRuleContexts(AdditiveExprContext);
		} else {
			return this.getRuleContext(i, AdditiveExprContext);
		}
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_relationalExpr; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterRelationalExpr) {
			listener.enterRelationalExpr(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitRelationalExpr) {
			listener.exitRelationalExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitRelationalExpr) {
			return visitor.visitRelationalExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class AdditiveExprContext extends ParserRuleContext {
	public multiplicativeExpr(): MultiplicativeExprContext[];
	public multiplicativeExpr(i: number): MultiplicativeExprContext;
	public multiplicativeExpr(i?: number): MultiplicativeExprContext | MultiplicativeExprContext[] {
		if (i === undefined) {
			return this.getRuleContexts(MultiplicativeExprContext);
		} else {
			return this.getRuleContext(i, MultiplicativeExprContext);
		}
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_additiveExpr; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterAdditiveExpr) {
			listener.enterAdditiveExpr(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitAdditiveExpr) {
			listener.exitAdditiveExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitAdditiveExpr) {
			return visitor.visitAdditiveExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class MultiplicativeExprContext extends ParserRuleContext {
	public unaryExpr(): UnaryExprContext[];
	public unaryExpr(i: number): UnaryExprContext;
	public unaryExpr(i?: number): UnaryExprContext | UnaryExprContext[] {
		if (i === undefined) {
			return this.getRuleContexts(UnaryExprContext);
		} else {
			return this.getRuleContext(i, UnaryExprContext);
		}
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_multiplicativeExpr; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterMultiplicativeExpr) {
			listener.enterMultiplicativeExpr(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitMultiplicativeExpr) {
			listener.exitMultiplicativeExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitMultiplicativeExpr) {
			return visitor.visitMultiplicativeExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class UnaryExprContext extends ParserRuleContext {
	public unaryExpr(): UnaryExprContext | undefined {
		return this.tryGetRuleContext(0, UnaryExprContext);
	}
	public primaryExpr(): PrimaryExprContext | undefined {
		return this.tryGetRuleContext(0, PrimaryExprContext);
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_unaryExpr; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterUnaryExpr) {
			listener.enterUnaryExpr(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitUnaryExpr) {
			listener.exitUnaryExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitUnaryExpr) {
			return visitor.visitUnaryExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class PrimaryExprContext extends ParserRuleContext {
	public literalExpr(): LiteralExprContext | undefined {
		return this.tryGetRuleContext(0, LiteralExprContext);
	}
	public leftHandSide(): LeftHandSideContext | undefined {
		return this.tryGetRuleContext(0, LeftHandSideContext);
	}
	public expression(): ExpressionContext | undefined {
		return this.tryGetRuleContext(0, ExpressionContext);
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_primaryExpr; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterPrimaryExpr) {
			listener.enterPrimaryExpr(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitPrimaryExpr) {
			listener.exitPrimaryExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitPrimaryExpr) {
			return visitor.visitPrimaryExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class LiteralExprContext extends ParserRuleContext {
	public Literal(): TerminalNode | undefined { return this.tryGetToken(CompiscriptParser.Literal, 0); }
	public arrayLiteral(): ArrayLiteralContext | undefined {
		return this.tryGetRuleContext(0, ArrayLiteralContext);
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_literalExpr; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterLiteralExpr) {
			listener.enterLiteralExpr(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitLiteralExpr) {
			listener.exitLiteralExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitLiteralExpr) {
			return visitor.visitLiteralExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class LeftHandSideContext extends ParserRuleContext {
	public primaryAtom(): PrimaryAtomContext {
		return this.getRuleContext(0, PrimaryAtomContext);
	}
	public suffixOp(): SuffixOpContext[];
	public suffixOp(i: number): SuffixOpContext;
	public suffixOp(i?: number): SuffixOpContext | SuffixOpContext[] {
		if (i === undefined) {
			return this.getRuleContexts(SuffixOpContext);
		} else {
			return this.getRuleContext(i, SuffixOpContext);
		}
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_leftHandSide; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterLeftHandSide) {
			listener.enterLeftHandSide(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitLeftHandSide) {
			listener.exitLeftHandSide(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitLeftHandSide) {
			return visitor.visitLeftHandSide(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class PrimaryAtomContext extends ParserRuleContext {
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_primaryAtom; }
	public copyFrom(ctx: PrimaryAtomContext): void {
		super.copyFrom(ctx);
	}
}
export class IdentifierExprContext extends PrimaryAtomContext {
	public Identifier(): TerminalNode { return this.getToken(CompiscriptParser.Identifier, 0); }
	constructor(ctx: PrimaryAtomContext) {
		super(ctx.parent, ctx.invokingState);
		this.copyFrom(ctx);
	}
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterIdentifierExpr) {
			listener.enterIdentifierExpr(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitIdentifierExpr) {
			listener.exitIdentifierExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitIdentifierExpr) {
			return visitor.visitIdentifierExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}
export class NewExprContext extends PrimaryAtomContext {
	public Identifier(): TerminalNode { return this.getToken(CompiscriptParser.Identifier, 0); }
	public arguments(): ArgumentsContext | undefined {
		return this.tryGetRuleContext(0, ArgumentsContext);
	}
	constructor(ctx: PrimaryAtomContext) {
		super(ctx.parent, ctx.invokingState);
		this.copyFrom(ctx);
	}
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterNewExpr) {
			listener.enterNewExpr(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitNewExpr) {
			listener.exitNewExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitNewExpr) {
			return visitor.visitNewExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}
export class ThisExprContext extends PrimaryAtomContext {
	constructor(ctx: PrimaryAtomContext) {
		super(ctx.parent, ctx.invokingState);
		this.copyFrom(ctx);
	}
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterThisExpr) {
			listener.enterThisExpr(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitThisExpr) {
			listener.exitThisExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitThisExpr) {
			return visitor.visitThisExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class SuffixOpContext extends ParserRuleContext {
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_suffixOp; }
	public copyFrom(ctx: SuffixOpContext): void {
		super.copyFrom(ctx);
	}
}
export class CallExprContext extends SuffixOpContext {
	public arguments(): ArgumentsContext | undefined {
		return this.tryGetRuleContext(0, ArgumentsContext);
	}
	constructor(ctx: SuffixOpContext) {
		super(ctx.parent, ctx.invokingState);
		this.copyFrom(ctx);
	}
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterCallExpr) {
			listener.enterCallExpr(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitCallExpr) {
			listener.exitCallExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitCallExpr) {
			return visitor.visitCallExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}
export class IndexExprContext extends SuffixOpContext {
	public expression(): ExpressionContext {
		return this.getRuleContext(0, ExpressionContext);
	}
	constructor(ctx: SuffixOpContext) {
		super(ctx.parent, ctx.invokingState);
		this.copyFrom(ctx);
	}
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterIndexExpr) {
			listener.enterIndexExpr(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitIndexExpr) {
			listener.exitIndexExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitIndexExpr) {
			return visitor.visitIndexExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}
export class PropertyAccessExprContext extends SuffixOpContext {
	public Identifier(): TerminalNode { return this.getToken(CompiscriptParser.Identifier, 0); }
	constructor(ctx: SuffixOpContext) {
		super(ctx.parent, ctx.invokingState);
		this.copyFrom(ctx);
	}
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterPropertyAccessExpr) {
			listener.enterPropertyAccessExpr(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitPropertyAccessExpr) {
			listener.exitPropertyAccessExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitPropertyAccessExpr) {
			return visitor.visitPropertyAccessExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class ArgumentsContext extends ParserRuleContext {
	public expression(): ExpressionContext[];
	public expression(i: number): ExpressionContext;
	public expression(i?: number): ExpressionContext | ExpressionContext[] {
		if (i === undefined) {
			return this.getRuleContexts(ExpressionContext);
		} else {
			return this.getRuleContext(i, ExpressionContext);
		}
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_arguments; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterArguments) {
			listener.enterArguments(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitArguments) {
			listener.exitArguments(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitArguments) {
			return visitor.visitArguments(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class ArrayLiteralContext extends ParserRuleContext {
	public expression(): ExpressionContext[];
	public expression(i: number): ExpressionContext;
	public expression(i?: number): ExpressionContext | ExpressionContext[] {
		if (i === undefined) {
			return this.getRuleContexts(ExpressionContext);
		} else {
			return this.getRuleContext(i, ExpressionContext);
		}
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_arrayLiteral; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterArrayLiteral) {
			listener.enterArrayLiteral(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitArrayLiteral) {
			listener.exitArrayLiteral(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitArrayLiteral) {
			return visitor.visitArrayLiteral(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class TypeContext extends ParserRuleContext {
	public baseType(): BaseTypeContext {
		return this.getRuleContext(0, BaseTypeContext);
	}
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_type; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterType) {
			listener.enterType(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitType) {
			listener.exitType(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitType) {
			return visitor.visitType(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class BaseTypeContext extends ParserRuleContext {
	public Identifier(): TerminalNode { return this.getToken(CompiscriptParser.Identifier, 0); }
	constructor(parent: ParserRuleContext | undefined, invokingState: number) {
		super(parent, invokingState);
	}
	// @Override
	public get ruleIndex(): number { return CompiscriptParser.RULE_baseType; }
	// @Override
	public enterRule(listener: CompiscriptListener): void {
		if (listener.enterBaseType) {
			listener.enterBaseType(this);
		}
	}
	// @Override
	public exitRule(listener: CompiscriptListener): void {
		if (listener.exitBaseType) {
			listener.exitBaseType(this);
		}
	}
	// @Override
	public accept<Result>(visitor: CompiscriptVisitor<Result>): Result {
		if (visitor.visitBaseType) {
			return visitor.visitBaseType(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


