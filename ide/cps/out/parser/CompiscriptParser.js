"use strict";
// Generated from src/grammar/Compiscript.g4 by ANTLR 4.9.0-SNAPSHOT
Object.defineProperty(exports, "__esModule", { value: true });
exports.SuffixOpContext = exports.ThisExprContext = exports.NewExprContext = exports.IdentifierExprContext = exports.PrimaryAtomContext = exports.LeftHandSideContext = exports.LiteralExprContext = exports.PrimaryExprContext = exports.UnaryExprContext = exports.MultiplicativeExprContext = exports.AdditiveExprContext = exports.RelationalExprContext = exports.EqualityExprContext = exports.LogicalAndExprContext = exports.LogicalOrExprContext = exports.TernaryExprContext = exports.ConditionalExprContext = exports.ExprNoAssignContext = exports.PropertyAssignExprContext = exports.AssignExprContext = exports.AssignmentExprContext = exports.ExpressionContext = exports.ClassMemberContext = exports.ClassDeclarationContext = exports.ParameterContext = exports.ParametersContext = exports.FunctionDeclarationContext = exports.DefaultCaseContext = exports.SwitchCaseContext = exports.SwitchStatementContext = exports.TryCatchStatementContext = exports.ReturnStatementContext = exports.ContinueStatementContext = exports.BreakStatementContext = exports.ForeachStatementContext = exports.ForStatementContext = exports.DoWhileStatementContext = exports.WhileStatementContext = exports.IfStatementContext = exports.PrintStatementContext = exports.ExpressionStatementContext = exports.AssignmentContext = exports.InitializerContext = exports.TypeAnnotationContext = exports.ConstantDeclarationContext = exports.VariableDeclarationContext = exports.BlockContext = exports.StatementContext = exports.ProgramContext = exports.CompiscriptParser = void 0;
exports.BaseTypeContext = exports.TypeContext = exports.ArrayLiteralContext = exports.ArgumentsContext = exports.PropertyAccessExprContext = exports.IndexExprContext = exports.CallExprContext = void 0;
const ATN_1 = require("antlr4ts/atn/ATN");
const ATNDeserializer_1 = require("antlr4ts/atn/ATNDeserializer");
const FailedPredicateException_1 = require("antlr4ts/FailedPredicateException");
const NoViableAltException_1 = require("antlr4ts/NoViableAltException");
const Parser_1 = require("antlr4ts/Parser");
const ParserRuleContext_1 = require("antlr4ts/ParserRuleContext");
const ParserATNSimulator_1 = require("antlr4ts/atn/ParserATNSimulator");
const RecognitionException_1 = require("antlr4ts/RecognitionException");
const Token_1 = require("antlr4ts/Token");
const VocabularyImpl_1 = require("antlr4ts/VocabularyImpl");
const Utils = require("antlr4ts/misc/Utils");
class CompiscriptParser extends Parser_1.Parser {
    // @Override
    // @NotNull
    get vocabulary() {
        return CompiscriptParser.VOCABULARY;
    }
    // tslint:enable:no-trailing-whitespace
    // @Override
    get grammarFileName() { return "Compiscript.g4"; }
    // @Override
    get ruleNames() { return CompiscriptParser.ruleNames; }
    // @Override
    get serializedATN() { return CompiscriptParser._serializedATN; }
    createFailedPredicateException(predicate, message) {
        return new FailedPredicateException_1.FailedPredicateException(this, predicate, message);
    }
    constructor(input) {
        super(input);
        this._interp = new ParserATNSimulator_1.ParserATNSimulator(CompiscriptParser._ATN, this);
    }
    // @RuleVersion(0)
    program() {
        let _localctx = new ProgramContext(this._ctx, this.state);
        this.enterRule(_localctx, 0, CompiscriptParser.RULE_program);
        let _la;
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    statement() {
        let _localctx = new StatementContext(this._ctx, this.state);
        this.enterRule(_localctx, 2, CompiscriptParser.RULE_statement);
        try {
            this.state = 118;
            this._errHandler.sync(this);
            switch (this.interpreter.adaptivePredict(this._input, 1, this._ctx)) {
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    block() {
        let _localctx = new BlockContext(this._ctx, this.state);
        this.enterRule(_localctx, 4, CompiscriptParser.RULE_block);
        let _la;
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    variableDeclaration() {
        let _localctx = new VariableDeclarationContext(this._ctx, this.state);
        this.enterRule(_localctx, 6, CompiscriptParser.RULE_variableDeclaration);
        let _la;
        try {
            this.enterOuterAlt(_localctx, 1);
            {
                this.state = 129;
                _la = this._input.LA(1);
                if (!(_la === CompiscriptParser.T__2 || _la === CompiscriptParser.T__3)) {
                    this._errHandler.recoverInline(this);
                }
                else {
                    if (this._input.LA(1) === Token_1.Token.EOF) {
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    constantDeclaration() {
        let _localctx = new ConstantDeclarationContext(this._ctx, this.state);
        this.enterRule(_localctx, 8, CompiscriptParser.RULE_constantDeclaration);
        let _la;
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    typeAnnotation() {
        let _localctx = new TypeAnnotationContext(this._ctx, this.state);
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    initializer() {
        let _localctx = new InitializerContext(this._ctx, this.state);
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    assignment() {
        let _localctx = new AssignmentContext(this._ctx, this.state);
        this.enterRule(_localctx, 14, CompiscriptParser.RULE_assignment);
        try {
            this.state = 166;
            this._errHandler.sync(this);
            switch (this.interpreter.adaptivePredict(this._input, 6, this._ctx)) {
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    expressionStatement() {
        let _localctx = new ExpressionStatementContext(this._ctx, this.state);
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    printStatement() {
        let _localctx = new PrintStatementContext(this._ctx, this.state);
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    ifStatement() {
        let _localctx = new IfStatementContext(this._ctx, this.state);
        this.enterRule(_localctx, 20, CompiscriptParser.RULE_ifStatement);
        let _la;
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    whileStatement() {
        let _localctx = new WhileStatementContext(this._ctx, this.state);
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    doWhileStatement() {
        let _localctx = new DoWhileStatementContext(this._ctx, this.state);
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    forStatement() {
        let _localctx = new ForStatementContext(this._ctx, this.state);
        this.enterRule(_localctx, 26, CompiscriptParser.RULE_forStatement);
        let _la;
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
                        throw new NoViableAltException_1.NoViableAltException(this);
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    foreachStatement() {
        let _localctx = new ForeachStatementContext(this._ctx, this.state);
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    breakStatement() {
        let _localctx = new BreakStatementContext(this._ctx, this.state);
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    continueStatement() {
        let _localctx = new ContinueStatementContext(this._ctx, this.state);
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    returnStatement() {
        let _localctx = new ReturnStatementContext(this._ctx, this.state);
        this.enterRule(_localctx, 34, CompiscriptParser.RULE_returnStatement);
        let _la;
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    tryCatchStatement() {
        let _localctx = new TryCatchStatementContext(this._ctx, this.state);
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    switchStatement() {
        let _localctx = new SwitchStatementContext(this._ctx, this.state);
        this.enterRule(_localctx, 38, CompiscriptParser.RULE_switchStatement);
        let _la;
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    switchCase() {
        let _localctx = new SwitchCaseContext(this._ctx, this.state);
        this.enterRule(_localctx, 40, CompiscriptParser.RULE_switchCase);
        let _la;
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    defaultCase() {
        let _localctx = new DefaultCaseContext(this._ctx, this.state);
        this.enterRule(_localctx, 42, CompiscriptParser.RULE_defaultCase);
        let _la;
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    functionDeclaration() {
        let _localctx = new FunctionDeclarationContext(this._ctx, this.state);
        this.enterRule(_localctx, 44, CompiscriptParser.RULE_functionDeclaration);
        let _la;
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    parameters() {
        let _localctx = new ParametersContext(this._ctx, this.state);
        this.enterRule(_localctx, 46, CompiscriptParser.RULE_parameters);
        let _la;
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    parameter() {
        let _localctx = new ParameterContext(this._ctx, this.state);
        this.enterRule(_localctx, 48, CompiscriptParser.RULE_parameter);
        let _la;
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    classDeclaration() {
        let _localctx = new ClassDeclarationContext(this._ctx, this.state);
        this.enterRule(_localctx, 50, CompiscriptParser.RULE_classDeclaration);
        let _la;
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    classMember() {
        let _localctx = new ClassMemberContext(this._ctx, this.state);
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
                    throw new NoViableAltException_1.NoViableAltException(this);
            }
        }
        catch (re) {
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    expression() {
        let _localctx = new ExpressionContext(this._ctx, this.state);
        this.enterRule(_localctx, 54, CompiscriptParser.RULE_expression);
        try {
            this.enterOuterAlt(_localctx, 1);
            {
                this.state = 324;
                this.assignmentExpr();
            }
        }
        catch (re) {
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    assignmentExpr() {
        let _localctx = new AssignmentExprContext(this._ctx, this.state);
        this.enterRule(_localctx, 56, CompiscriptParser.RULE_assignmentExpr);
        try {
            this.state = 337;
            this._errHandler.sync(this);
            switch (this.interpreter.adaptivePredict(this._input, 23, this._ctx)) {
                case 1:
                    _localctx = new AssignExprContext(_localctx);
                    this.enterOuterAlt(_localctx, 1);
                    {
                        this.state = 326;
                        _localctx._lhs = this.leftHandSide();
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
                        _localctx._lhs = this.leftHandSide();
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    conditionalExpr() {
        let _localctx = new ConditionalExprContext(this._ctx, this.state);
        this.enterRule(_localctx, 58, CompiscriptParser.RULE_conditionalExpr);
        let _la;
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    logicalOrExpr() {
        let _localctx = new LogicalOrExprContext(this._ctx, this.state);
        this.enterRule(_localctx, 60, CompiscriptParser.RULE_logicalOrExpr);
        let _la;
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    logicalAndExpr() {
        let _localctx = new LogicalAndExprContext(this._ctx, this.state);
        this.enterRule(_localctx, 62, CompiscriptParser.RULE_logicalAndExpr);
        let _la;
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    equalityExpr() {
        let _localctx = new EqualityExprContext(this._ctx, this.state);
        this.enterRule(_localctx, 64, CompiscriptParser.RULE_equalityExpr);
        let _la;
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
                            }
                            else {
                                if (this._input.LA(1) === Token_1.Token.EOF) {
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    relationalExpr() {
        let _localctx = new RelationalExprContext(this._ctx, this.state);
        this.enterRule(_localctx, 66, CompiscriptParser.RULE_relationalExpr);
        let _la;
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
                            }
                            else {
                                if (this._input.LA(1) === Token_1.Token.EOF) {
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    additiveExpr() {
        let _localctx = new AdditiveExprContext(this._ctx, this.state);
        this.enterRule(_localctx, 68, CompiscriptParser.RULE_additiveExpr);
        let _la;
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
                            }
                            else {
                                if (this._input.LA(1) === Token_1.Token.EOF) {
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    multiplicativeExpr() {
        let _localctx = new MultiplicativeExprContext(this._ctx, this.state);
        this.enterRule(_localctx, 70, CompiscriptParser.RULE_multiplicativeExpr);
        let _la;
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
                            }
                            else {
                                if (this._input.LA(1) === Token_1.Token.EOF) {
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    unaryExpr() {
        let _localctx = new UnaryExprContext(this._ctx, this.state);
        this.enterRule(_localctx, 72, CompiscriptParser.RULE_unaryExpr);
        let _la;
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
                        }
                        else {
                            if (this._input.LA(1) === Token_1.Token.EOF) {
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
                    throw new NoViableAltException_1.NoViableAltException(this);
            }
        }
        catch (re) {
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    primaryExpr() {
        let _localctx = new PrimaryExprContext(this._ctx, this.state);
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
                    throw new NoViableAltException_1.NoViableAltException(this);
            }
        }
        catch (re) {
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    literalExpr() {
        let _localctx = new LiteralExprContext(this._ctx, this.state);
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
                    throw new NoViableAltException_1.NoViableAltException(this);
            }
        }
        catch (re) {
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    leftHandSide() {
        let _localctx = new LeftHandSideContext(this._ctx, this.state);
        this.enterRule(_localctx, 78, CompiscriptParser.RULE_leftHandSide);
        try {
            let _alt;
            this.enterOuterAlt(_localctx, 1);
            {
                this.state = 415;
                this.primaryAtom();
                this.state = 419;
                this._errHandler.sync(this);
                _alt = this.interpreter.adaptivePredict(this._input, 34, this._ctx);
                while (_alt !== 2 && _alt !== ATN_1.ATN.INVALID_ALT_NUMBER) {
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    primaryAtom() {
        let _localctx = new PrimaryAtomContext(this._ctx, this.state);
        this.enterRule(_localctx, 80, CompiscriptParser.RULE_primaryAtom);
        let _la;
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
                    throw new NoViableAltException_1.NoViableAltException(this);
            }
        }
        catch (re) {
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    suffixOp() {
        let _localctx = new SuffixOpContext(this._ctx, this.state);
        this.enterRule(_localctx, 82, CompiscriptParser.RULE_suffixOp);
        let _la;
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
                    throw new NoViableAltException_1.NoViableAltException(this);
            }
        }
        catch (re) {
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    arguments() {
        let _localctx = new ArgumentsContext(this._ctx, this.state);
        this.enterRule(_localctx, 84, CompiscriptParser.RULE_arguments);
        let _la;
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    arrayLiteral() {
        let _localctx = new ArrayLiteralContext(this._ctx, this.state);
        this.enterRule(_localctx, 86, CompiscriptParser.RULE_arrayLiteral);
        let _la;
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    type() {
        let _localctx = new TypeContext(this._ctx, this.state);
        this.enterRule(_localctx, 88, CompiscriptParser.RULE_type);
        let _la;
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
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    // @RuleVersion(0)
    baseType() {
        let _localctx = new BaseTypeContext(this._ctx, this.state);
        this.enterRule(_localctx, 90, CompiscriptParser.RULE_baseType);
        let _la;
        try {
            this.enterOuterAlt(_localctx, 1);
            {
                this.state = 475;
                _la = this._input.LA(1);
                if (!(((((_la - 53)) & ~0x1F) === 0 && ((1 << (_la - 53)) & ((1 << (CompiscriptParser.T__52 - 53)) | (1 << (CompiscriptParser.T__53 - 53)) | (1 << (CompiscriptParser.T__54 - 53)) | (1 << (CompiscriptParser.Identifier - 53)))) !== 0))) {
                    this._errHandler.recoverInline(this);
                }
                else {
                    if (this._input.LA(1) === Token_1.Token.EOF) {
                        this.matchedEOF = true;
                    }
                    this._errHandler.reportMatch(this);
                    this.consume();
                }
            }
        }
        catch (re) {
            if (re instanceof RecognitionException_1.RecognitionException) {
                _localctx.exception = re;
                this._errHandler.reportError(this, re);
                this._errHandler.recover(this, re);
            }
            else {
                throw re;
            }
        }
        finally {
            this.exitRule();
        }
        return _localctx;
    }
    static get _ATN() {
        if (!CompiscriptParser.__ATN) {
            CompiscriptParser.__ATN = new ATNDeserializer_1.ATNDeserializer().deserialize(Utils.toCharArray(CompiscriptParser._serializedATN));
        }
        return CompiscriptParser.__ATN;
    }
}
exports.CompiscriptParser = CompiscriptParser;
CompiscriptParser.T__0 = 1;
CompiscriptParser.T__1 = 2;
CompiscriptParser.T__2 = 3;
CompiscriptParser.T__3 = 4;
CompiscriptParser.T__4 = 5;
CompiscriptParser.T__5 = 6;
CompiscriptParser.T__6 = 7;
CompiscriptParser.T__7 = 8;
CompiscriptParser.T__8 = 9;
CompiscriptParser.T__9 = 10;
CompiscriptParser.T__10 = 11;
CompiscriptParser.T__11 = 12;
CompiscriptParser.T__12 = 13;
CompiscriptParser.T__13 = 14;
CompiscriptParser.T__14 = 15;
CompiscriptParser.T__15 = 16;
CompiscriptParser.T__16 = 17;
CompiscriptParser.T__17 = 18;
CompiscriptParser.T__18 = 19;
CompiscriptParser.T__19 = 20;
CompiscriptParser.T__20 = 21;
CompiscriptParser.T__21 = 22;
CompiscriptParser.T__22 = 23;
CompiscriptParser.T__23 = 24;
CompiscriptParser.T__24 = 25;
CompiscriptParser.T__25 = 26;
CompiscriptParser.T__26 = 27;
CompiscriptParser.T__27 = 28;
CompiscriptParser.T__28 = 29;
CompiscriptParser.T__29 = 30;
CompiscriptParser.T__30 = 31;
CompiscriptParser.T__31 = 32;
CompiscriptParser.T__32 = 33;
CompiscriptParser.T__33 = 34;
CompiscriptParser.T__34 = 35;
CompiscriptParser.T__35 = 36;
CompiscriptParser.T__36 = 37;
CompiscriptParser.T__37 = 38;
CompiscriptParser.T__38 = 39;
CompiscriptParser.T__39 = 40;
CompiscriptParser.T__40 = 41;
CompiscriptParser.T__41 = 42;
CompiscriptParser.T__42 = 43;
CompiscriptParser.T__43 = 44;
CompiscriptParser.T__44 = 45;
CompiscriptParser.T__45 = 46;
CompiscriptParser.T__46 = 47;
CompiscriptParser.T__47 = 48;
CompiscriptParser.T__48 = 49;
CompiscriptParser.T__49 = 50;
CompiscriptParser.T__50 = 51;
CompiscriptParser.T__51 = 52;
CompiscriptParser.T__52 = 53;
CompiscriptParser.T__53 = 54;
CompiscriptParser.T__54 = 55;
CompiscriptParser.Literal = 56;
CompiscriptParser.IntegerLiteral = 57;
CompiscriptParser.StringLiteral = 58;
CompiscriptParser.Identifier = 59;
CompiscriptParser.WS = 60;
CompiscriptParser.COMMENT = 61;
CompiscriptParser.MULTILINE_COMMENT = 62;
CompiscriptParser.RULE_program = 0;
CompiscriptParser.RULE_statement = 1;
CompiscriptParser.RULE_block = 2;
CompiscriptParser.RULE_variableDeclaration = 3;
CompiscriptParser.RULE_constantDeclaration = 4;
CompiscriptParser.RULE_typeAnnotation = 5;
CompiscriptParser.RULE_initializer = 6;
CompiscriptParser.RULE_assignment = 7;
CompiscriptParser.RULE_expressionStatement = 8;
CompiscriptParser.RULE_printStatement = 9;
CompiscriptParser.RULE_ifStatement = 10;
CompiscriptParser.RULE_whileStatement = 11;
CompiscriptParser.RULE_doWhileStatement = 12;
CompiscriptParser.RULE_forStatement = 13;
CompiscriptParser.RULE_foreachStatement = 14;
CompiscriptParser.RULE_breakStatement = 15;
CompiscriptParser.RULE_continueStatement = 16;
CompiscriptParser.RULE_returnStatement = 17;
CompiscriptParser.RULE_tryCatchStatement = 18;
CompiscriptParser.RULE_switchStatement = 19;
CompiscriptParser.RULE_switchCase = 20;
CompiscriptParser.RULE_defaultCase = 21;
CompiscriptParser.RULE_functionDeclaration = 22;
CompiscriptParser.RULE_parameters = 23;
CompiscriptParser.RULE_parameter = 24;
CompiscriptParser.RULE_classDeclaration = 25;
CompiscriptParser.RULE_classMember = 26;
CompiscriptParser.RULE_expression = 27;
CompiscriptParser.RULE_assignmentExpr = 28;
CompiscriptParser.RULE_conditionalExpr = 29;
CompiscriptParser.RULE_logicalOrExpr = 30;
CompiscriptParser.RULE_logicalAndExpr = 31;
CompiscriptParser.RULE_equalityExpr = 32;
CompiscriptParser.RULE_relationalExpr = 33;
CompiscriptParser.RULE_additiveExpr = 34;
CompiscriptParser.RULE_multiplicativeExpr = 35;
CompiscriptParser.RULE_unaryExpr = 36;
CompiscriptParser.RULE_primaryExpr = 37;
CompiscriptParser.RULE_literalExpr = 38;
CompiscriptParser.RULE_leftHandSide = 39;
CompiscriptParser.RULE_primaryAtom = 40;
CompiscriptParser.RULE_suffixOp = 41;
CompiscriptParser.RULE_arguments = 42;
CompiscriptParser.RULE_arrayLiteral = 43;
CompiscriptParser.RULE_type = 44;
CompiscriptParser.RULE_baseType = 45;
// tslint:disable:no-trailing-whitespace
CompiscriptParser.ruleNames = [
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
CompiscriptParser._LITERAL_NAMES = [
    undefined, "'{'", "'}'", "'let'", "'var'", "';'", "'const'", "'='", "':'",
    "'.'", "'print'", "'('", "')'", "'if'", "'else'", "'while'", "'do'", "'for'",
    "'foreach'", "'in'", "'break'", "'continue'", "'return'", "'try'", "'catch'",
    "'switch'", "'case'", "'default'", "'function'", "','", "'class'", "'?'",
    "'||'", "'&&'", "'=='", "'!='", "'<'", "'<='", "'>'", "'>='", "'+'", "'-'",
    "'*'", "'/'", "'%'", "'!'", "'null'", "'true'", "'false'", "'new'", "'this'",
    "'['", "']'", "'boolean'", "'integer'", "'string'",
];
CompiscriptParser._SYMBOLIC_NAMES = [
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
CompiscriptParser.VOCABULARY = new VocabularyImpl_1.VocabularyImpl(CompiscriptParser._LITERAL_NAMES, CompiscriptParser._SYMBOLIC_NAMES, []);
CompiscriptParser._serializedATN = "\x03\uC91D\uCABA\u058D\uAFBA\u4F53\u0607\uEA8B\uC241\x03@\u01E0\x04\x02" +
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
class ProgramContext extends ParserRuleContext_1.ParserRuleContext {
    EOF() { return this.getToken(CompiscriptParser.EOF, 0); }
    statement(i) {
        if (i === undefined) {
            return this.getRuleContexts(StatementContext);
        }
        else {
            return this.getRuleContext(i, StatementContext);
        }
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_program; }
    // @Override
    enterRule(listener) {
        if (listener.enterProgram) {
            listener.enterProgram(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitProgram) {
            listener.exitProgram(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitProgram) {
            return visitor.visitProgram(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.ProgramContext = ProgramContext;
class StatementContext extends ParserRuleContext_1.ParserRuleContext {
    variableDeclaration() {
        return this.tryGetRuleContext(0, VariableDeclarationContext);
    }
    constantDeclaration() {
        return this.tryGetRuleContext(0, ConstantDeclarationContext);
    }
    assignment() {
        return this.tryGetRuleContext(0, AssignmentContext);
    }
    functionDeclaration() {
        return this.tryGetRuleContext(0, FunctionDeclarationContext);
    }
    classDeclaration() {
        return this.tryGetRuleContext(0, ClassDeclarationContext);
    }
    expressionStatement() {
        return this.tryGetRuleContext(0, ExpressionStatementContext);
    }
    printStatement() {
        return this.tryGetRuleContext(0, PrintStatementContext);
    }
    block() {
        return this.tryGetRuleContext(0, BlockContext);
    }
    ifStatement() {
        return this.tryGetRuleContext(0, IfStatementContext);
    }
    whileStatement() {
        return this.tryGetRuleContext(0, WhileStatementContext);
    }
    doWhileStatement() {
        return this.tryGetRuleContext(0, DoWhileStatementContext);
    }
    forStatement() {
        return this.tryGetRuleContext(0, ForStatementContext);
    }
    foreachStatement() {
        return this.tryGetRuleContext(0, ForeachStatementContext);
    }
    tryCatchStatement() {
        return this.tryGetRuleContext(0, TryCatchStatementContext);
    }
    switchStatement() {
        return this.tryGetRuleContext(0, SwitchStatementContext);
    }
    breakStatement() {
        return this.tryGetRuleContext(0, BreakStatementContext);
    }
    continueStatement() {
        return this.tryGetRuleContext(0, ContinueStatementContext);
    }
    returnStatement() {
        return this.tryGetRuleContext(0, ReturnStatementContext);
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_statement; }
    // @Override
    enterRule(listener) {
        if (listener.enterStatement) {
            listener.enterStatement(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitStatement) {
            listener.exitStatement(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitStatement) {
            return visitor.visitStatement(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.StatementContext = StatementContext;
class BlockContext extends ParserRuleContext_1.ParserRuleContext {
    statement(i) {
        if (i === undefined) {
            return this.getRuleContexts(StatementContext);
        }
        else {
            return this.getRuleContext(i, StatementContext);
        }
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_block; }
    // @Override
    enterRule(listener) {
        if (listener.enterBlock) {
            listener.enterBlock(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitBlock) {
            listener.exitBlock(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitBlock) {
            return visitor.visitBlock(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.BlockContext = BlockContext;
class VariableDeclarationContext extends ParserRuleContext_1.ParserRuleContext {
    Identifier() { return this.getToken(CompiscriptParser.Identifier, 0); }
    typeAnnotation() {
        return this.tryGetRuleContext(0, TypeAnnotationContext);
    }
    initializer() {
        return this.tryGetRuleContext(0, InitializerContext);
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_variableDeclaration; }
    // @Override
    enterRule(listener) {
        if (listener.enterVariableDeclaration) {
            listener.enterVariableDeclaration(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitVariableDeclaration) {
            listener.exitVariableDeclaration(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitVariableDeclaration) {
            return visitor.visitVariableDeclaration(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.VariableDeclarationContext = VariableDeclarationContext;
class ConstantDeclarationContext extends ParserRuleContext_1.ParserRuleContext {
    Identifier() { return this.getToken(CompiscriptParser.Identifier, 0); }
    expression() {
        return this.getRuleContext(0, ExpressionContext);
    }
    typeAnnotation() {
        return this.tryGetRuleContext(0, TypeAnnotationContext);
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_constantDeclaration; }
    // @Override
    enterRule(listener) {
        if (listener.enterConstantDeclaration) {
            listener.enterConstantDeclaration(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitConstantDeclaration) {
            listener.exitConstantDeclaration(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitConstantDeclaration) {
            return visitor.visitConstantDeclaration(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.ConstantDeclarationContext = ConstantDeclarationContext;
class TypeAnnotationContext extends ParserRuleContext_1.ParserRuleContext {
    type() {
        return this.getRuleContext(0, TypeContext);
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_typeAnnotation; }
    // @Override
    enterRule(listener) {
        if (listener.enterTypeAnnotation) {
            listener.enterTypeAnnotation(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitTypeAnnotation) {
            listener.exitTypeAnnotation(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitTypeAnnotation) {
            return visitor.visitTypeAnnotation(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.TypeAnnotationContext = TypeAnnotationContext;
class InitializerContext extends ParserRuleContext_1.ParserRuleContext {
    expression() {
        return this.getRuleContext(0, ExpressionContext);
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_initializer; }
    // @Override
    enterRule(listener) {
        if (listener.enterInitializer) {
            listener.enterInitializer(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitInitializer) {
            listener.exitInitializer(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitInitializer) {
            return visitor.visitInitializer(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.InitializerContext = InitializerContext;
class AssignmentContext extends ParserRuleContext_1.ParserRuleContext {
    Identifier() { return this.getToken(CompiscriptParser.Identifier, 0); }
    expression(i) {
        if (i === undefined) {
            return this.getRuleContexts(ExpressionContext);
        }
        else {
            return this.getRuleContext(i, ExpressionContext);
        }
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_assignment; }
    // @Override
    enterRule(listener) {
        if (listener.enterAssignment) {
            listener.enterAssignment(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitAssignment) {
            listener.exitAssignment(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitAssignment) {
            return visitor.visitAssignment(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.AssignmentContext = AssignmentContext;
class ExpressionStatementContext extends ParserRuleContext_1.ParserRuleContext {
    expression() {
        return this.getRuleContext(0, ExpressionContext);
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_expressionStatement; }
    // @Override
    enterRule(listener) {
        if (listener.enterExpressionStatement) {
            listener.enterExpressionStatement(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitExpressionStatement) {
            listener.exitExpressionStatement(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitExpressionStatement) {
            return visitor.visitExpressionStatement(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.ExpressionStatementContext = ExpressionStatementContext;
class PrintStatementContext extends ParserRuleContext_1.ParserRuleContext {
    expression() {
        return this.getRuleContext(0, ExpressionContext);
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_printStatement; }
    // @Override
    enterRule(listener) {
        if (listener.enterPrintStatement) {
            listener.enterPrintStatement(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitPrintStatement) {
            listener.exitPrintStatement(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitPrintStatement) {
            return visitor.visitPrintStatement(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.PrintStatementContext = PrintStatementContext;
class IfStatementContext extends ParserRuleContext_1.ParserRuleContext {
    expression() {
        return this.getRuleContext(0, ExpressionContext);
    }
    block(i) {
        if (i === undefined) {
            return this.getRuleContexts(BlockContext);
        }
        else {
            return this.getRuleContext(i, BlockContext);
        }
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_ifStatement; }
    // @Override
    enterRule(listener) {
        if (listener.enterIfStatement) {
            listener.enterIfStatement(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitIfStatement) {
            listener.exitIfStatement(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitIfStatement) {
            return visitor.visitIfStatement(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.IfStatementContext = IfStatementContext;
class WhileStatementContext extends ParserRuleContext_1.ParserRuleContext {
    expression() {
        return this.getRuleContext(0, ExpressionContext);
    }
    block() {
        return this.getRuleContext(0, BlockContext);
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_whileStatement; }
    // @Override
    enterRule(listener) {
        if (listener.enterWhileStatement) {
            listener.enterWhileStatement(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitWhileStatement) {
            listener.exitWhileStatement(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitWhileStatement) {
            return visitor.visitWhileStatement(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.WhileStatementContext = WhileStatementContext;
class DoWhileStatementContext extends ParserRuleContext_1.ParserRuleContext {
    block() {
        return this.getRuleContext(0, BlockContext);
    }
    expression() {
        return this.getRuleContext(0, ExpressionContext);
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_doWhileStatement; }
    // @Override
    enterRule(listener) {
        if (listener.enterDoWhileStatement) {
            listener.enterDoWhileStatement(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitDoWhileStatement) {
            listener.exitDoWhileStatement(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitDoWhileStatement) {
            return visitor.visitDoWhileStatement(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.DoWhileStatementContext = DoWhileStatementContext;
class ForStatementContext extends ParserRuleContext_1.ParserRuleContext {
    block() {
        return this.getRuleContext(0, BlockContext);
    }
    variableDeclaration() {
        return this.tryGetRuleContext(0, VariableDeclarationContext);
    }
    assignment() {
        return this.tryGetRuleContext(0, AssignmentContext);
    }
    expression(i) {
        if (i === undefined) {
            return this.getRuleContexts(ExpressionContext);
        }
        else {
            return this.getRuleContext(i, ExpressionContext);
        }
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_forStatement; }
    // @Override
    enterRule(listener) {
        if (listener.enterForStatement) {
            listener.enterForStatement(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitForStatement) {
            listener.exitForStatement(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitForStatement) {
            return visitor.visitForStatement(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.ForStatementContext = ForStatementContext;
class ForeachStatementContext extends ParserRuleContext_1.ParserRuleContext {
    Identifier() { return this.getToken(CompiscriptParser.Identifier, 0); }
    expression() {
        return this.getRuleContext(0, ExpressionContext);
    }
    block() {
        return this.getRuleContext(0, BlockContext);
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_foreachStatement; }
    // @Override
    enterRule(listener) {
        if (listener.enterForeachStatement) {
            listener.enterForeachStatement(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitForeachStatement) {
            listener.exitForeachStatement(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitForeachStatement) {
            return visitor.visitForeachStatement(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.ForeachStatementContext = ForeachStatementContext;
class BreakStatementContext extends ParserRuleContext_1.ParserRuleContext {
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_breakStatement; }
    // @Override
    enterRule(listener) {
        if (listener.enterBreakStatement) {
            listener.enterBreakStatement(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitBreakStatement) {
            listener.exitBreakStatement(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitBreakStatement) {
            return visitor.visitBreakStatement(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.BreakStatementContext = BreakStatementContext;
class ContinueStatementContext extends ParserRuleContext_1.ParserRuleContext {
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_continueStatement; }
    // @Override
    enterRule(listener) {
        if (listener.enterContinueStatement) {
            listener.enterContinueStatement(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitContinueStatement) {
            listener.exitContinueStatement(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitContinueStatement) {
            return visitor.visitContinueStatement(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.ContinueStatementContext = ContinueStatementContext;
class ReturnStatementContext extends ParserRuleContext_1.ParserRuleContext {
    expression() {
        return this.tryGetRuleContext(0, ExpressionContext);
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_returnStatement; }
    // @Override
    enterRule(listener) {
        if (listener.enterReturnStatement) {
            listener.enterReturnStatement(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitReturnStatement) {
            listener.exitReturnStatement(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitReturnStatement) {
            return visitor.visitReturnStatement(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.ReturnStatementContext = ReturnStatementContext;
class TryCatchStatementContext extends ParserRuleContext_1.ParserRuleContext {
    block(i) {
        if (i === undefined) {
            return this.getRuleContexts(BlockContext);
        }
        else {
            return this.getRuleContext(i, BlockContext);
        }
    }
    Identifier() { return this.getToken(CompiscriptParser.Identifier, 0); }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_tryCatchStatement; }
    // @Override
    enterRule(listener) {
        if (listener.enterTryCatchStatement) {
            listener.enterTryCatchStatement(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitTryCatchStatement) {
            listener.exitTryCatchStatement(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitTryCatchStatement) {
            return visitor.visitTryCatchStatement(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.TryCatchStatementContext = TryCatchStatementContext;
class SwitchStatementContext extends ParserRuleContext_1.ParserRuleContext {
    expression() {
        return this.getRuleContext(0, ExpressionContext);
    }
    switchCase(i) {
        if (i === undefined) {
            return this.getRuleContexts(SwitchCaseContext);
        }
        else {
            return this.getRuleContext(i, SwitchCaseContext);
        }
    }
    defaultCase() {
        return this.tryGetRuleContext(0, DefaultCaseContext);
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_switchStatement; }
    // @Override
    enterRule(listener) {
        if (listener.enterSwitchStatement) {
            listener.enterSwitchStatement(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitSwitchStatement) {
            listener.exitSwitchStatement(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitSwitchStatement) {
            return visitor.visitSwitchStatement(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.SwitchStatementContext = SwitchStatementContext;
class SwitchCaseContext extends ParserRuleContext_1.ParserRuleContext {
    expression() {
        return this.getRuleContext(0, ExpressionContext);
    }
    statement(i) {
        if (i === undefined) {
            return this.getRuleContexts(StatementContext);
        }
        else {
            return this.getRuleContext(i, StatementContext);
        }
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_switchCase; }
    // @Override
    enterRule(listener) {
        if (listener.enterSwitchCase) {
            listener.enterSwitchCase(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitSwitchCase) {
            listener.exitSwitchCase(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitSwitchCase) {
            return visitor.visitSwitchCase(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.SwitchCaseContext = SwitchCaseContext;
class DefaultCaseContext extends ParserRuleContext_1.ParserRuleContext {
    statement(i) {
        if (i === undefined) {
            return this.getRuleContexts(StatementContext);
        }
        else {
            return this.getRuleContext(i, StatementContext);
        }
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_defaultCase; }
    // @Override
    enterRule(listener) {
        if (listener.enterDefaultCase) {
            listener.enterDefaultCase(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitDefaultCase) {
            listener.exitDefaultCase(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitDefaultCase) {
            return visitor.visitDefaultCase(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.DefaultCaseContext = DefaultCaseContext;
class FunctionDeclarationContext extends ParserRuleContext_1.ParserRuleContext {
    Identifier() { return this.getToken(CompiscriptParser.Identifier, 0); }
    block() {
        return this.getRuleContext(0, BlockContext);
    }
    parameters() {
        return this.tryGetRuleContext(0, ParametersContext);
    }
    type() {
        return this.tryGetRuleContext(0, TypeContext);
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_functionDeclaration; }
    // @Override
    enterRule(listener) {
        if (listener.enterFunctionDeclaration) {
            listener.enterFunctionDeclaration(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitFunctionDeclaration) {
            listener.exitFunctionDeclaration(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitFunctionDeclaration) {
            return visitor.visitFunctionDeclaration(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.FunctionDeclarationContext = FunctionDeclarationContext;
class ParametersContext extends ParserRuleContext_1.ParserRuleContext {
    parameter(i) {
        if (i === undefined) {
            return this.getRuleContexts(ParameterContext);
        }
        else {
            return this.getRuleContext(i, ParameterContext);
        }
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_parameters; }
    // @Override
    enterRule(listener) {
        if (listener.enterParameters) {
            listener.enterParameters(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitParameters) {
            listener.exitParameters(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitParameters) {
            return visitor.visitParameters(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.ParametersContext = ParametersContext;
class ParameterContext extends ParserRuleContext_1.ParserRuleContext {
    Identifier() { return this.getToken(CompiscriptParser.Identifier, 0); }
    type() {
        return this.tryGetRuleContext(0, TypeContext);
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_parameter; }
    // @Override
    enterRule(listener) {
        if (listener.enterParameter) {
            listener.enterParameter(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitParameter) {
            listener.exitParameter(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitParameter) {
            return visitor.visitParameter(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.ParameterContext = ParameterContext;
class ClassDeclarationContext extends ParserRuleContext_1.ParserRuleContext {
    Identifier(i) {
        if (i === undefined) {
            return this.getTokens(CompiscriptParser.Identifier);
        }
        else {
            return this.getToken(CompiscriptParser.Identifier, i);
        }
    }
    classMember(i) {
        if (i === undefined) {
            return this.getRuleContexts(ClassMemberContext);
        }
        else {
            return this.getRuleContext(i, ClassMemberContext);
        }
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_classDeclaration; }
    // @Override
    enterRule(listener) {
        if (listener.enterClassDeclaration) {
            listener.enterClassDeclaration(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitClassDeclaration) {
            listener.exitClassDeclaration(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitClassDeclaration) {
            return visitor.visitClassDeclaration(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.ClassDeclarationContext = ClassDeclarationContext;
class ClassMemberContext extends ParserRuleContext_1.ParserRuleContext {
    functionDeclaration() {
        return this.tryGetRuleContext(0, FunctionDeclarationContext);
    }
    variableDeclaration() {
        return this.tryGetRuleContext(0, VariableDeclarationContext);
    }
    constantDeclaration() {
        return this.tryGetRuleContext(0, ConstantDeclarationContext);
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_classMember; }
    // @Override
    enterRule(listener) {
        if (listener.enterClassMember) {
            listener.enterClassMember(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitClassMember) {
            listener.exitClassMember(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitClassMember) {
            return visitor.visitClassMember(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.ClassMemberContext = ClassMemberContext;
class ExpressionContext extends ParserRuleContext_1.ParserRuleContext {
    assignmentExpr() {
        return this.getRuleContext(0, AssignmentExprContext);
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_expression; }
    // @Override
    enterRule(listener) {
        if (listener.enterExpression) {
            listener.enterExpression(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitExpression) {
            listener.exitExpression(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitExpression) {
            return visitor.visitExpression(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.ExpressionContext = ExpressionContext;
class AssignmentExprContext extends ParserRuleContext_1.ParserRuleContext {
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_assignmentExpr; }
    copyFrom(ctx) {
        super.copyFrom(ctx);
    }
}
exports.AssignmentExprContext = AssignmentExprContext;
class AssignExprContext extends AssignmentExprContext {
    assignmentExpr() {
        return this.getRuleContext(0, AssignmentExprContext);
    }
    leftHandSide() {
        return this.getRuleContext(0, LeftHandSideContext);
    }
    constructor(ctx) {
        super(ctx.parent, ctx.invokingState);
        this.copyFrom(ctx);
    }
    // @Override
    enterRule(listener) {
        if (listener.enterAssignExpr) {
            listener.enterAssignExpr(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitAssignExpr) {
            listener.exitAssignExpr(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitAssignExpr) {
            return visitor.visitAssignExpr(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.AssignExprContext = AssignExprContext;
class PropertyAssignExprContext extends AssignmentExprContext {
    Identifier() { return this.getToken(CompiscriptParser.Identifier, 0); }
    assignmentExpr() {
        return this.getRuleContext(0, AssignmentExprContext);
    }
    leftHandSide() {
        return this.getRuleContext(0, LeftHandSideContext);
    }
    constructor(ctx) {
        super(ctx.parent, ctx.invokingState);
        this.copyFrom(ctx);
    }
    // @Override
    enterRule(listener) {
        if (listener.enterPropertyAssignExpr) {
            listener.enterPropertyAssignExpr(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitPropertyAssignExpr) {
            listener.exitPropertyAssignExpr(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitPropertyAssignExpr) {
            return visitor.visitPropertyAssignExpr(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.PropertyAssignExprContext = PropertyAssignExprContext;
class ExprNoAssignContext extends AssignmentExprContext {
    conditionalExpr() {
        return this.getRuleContext(0, ConditionalExprContext);
    }
    constructor(ctx) {
        super(ctx.parent, ctx.invokingState);
        this.copyFrom(ctx);
    }
    // @Override
    enterRule(listener) {
        if (listener.enterExprNoAssign) {
            listener.enterExprNoAssign(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitExprNoAssign) {
            listener.exitExprNoAssign(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitExprNoAssign) {
            return visitor.visitExprNoAssign(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.ExprNoAssignContext = ExprNoAssignContext;
class ConditionalExprContext extends ParserRuleContext_1.ParserRuleContext {
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_conditionalExpr; }
    copyFrom(ctx) {
        super.copyFrom(ctx);
    }
}
exports.ConditionalExprContext = ConditionalExprContext;
class TernaryExprContext extends ConditionalExprContext {
    logicalOrExpr() {
        return this.getRuleContext(0, LogicalOrExprContext);
    }
    expression(i) {
        if (i === undefined) {
            return this.getRuleContexts(ExpressionContext);
        }
        else {
            return this.getRuleContext(i, ExpressionContext);
        }
    }
    constructor(ctx) {
        super(ctx.parent, ctx.invokingState);
        this.copyFrom(ctx);
    }
    // @Override
    enterRule(listener) {
        if (listener.enterTernaryExpr) {
            listener.enterTernaryExpr(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitTernaryExpr) {
            listener.exitTernaryExpr(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitTernaryExpr) {
            return visitor.visitTernaryExpr(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.TernaryExprContext = TernaryExprContext;
class LogicalOrExprContext extends ParserRuleContext_1.ParserRuleContext {
    logicalAndExpr(i) {
        if (i === undefined) {
            return this.getRuleContexts(LogicalAndExprContext);
        }
        else {
            return this.getRuleContext(i, LogicalAndExprContext);
        }
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_logicalOrExpr; }
    // @Override
    enterRule(listener) {
        if (listener.enterLogicalOrExpr) {
            listener.enterLogicalOrExpr(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitLogicalOrExpr) {
            listener.exitLogicalOrExpr(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitLogicalOrExpr) {
            return visitor.visitLogicalOrExpr(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.LogicalOrExprContext = LogicalOrExprContext;
class LogicalAndExprContext extends ParserRuleContext_1.ParserRuleContext {
    equalityExpr(i) {
        if (i === undefined) {
            return this.getRuleContexts(EqualityExprContext);
        }
        else {
            return this.getRuleContext(i, EqualityExprContext);
        }
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_logicalAndExpr; }
    // @Override
    enterRule(listener) {
        if (listener.enterLogicalAndExpr) {
            listener.enterLogicalAndExpr(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitLogicalAndExpr) {
            listener.exitLogicalAndExpr(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitLogicalAndExpr) {
            return visitor.visitLogicalAndExpr(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.LogicalAndExprContext = LogicalAndExprContext;
class EqualityExprContext extends ParserRuleContext_1.ParserRuleContext {
    relationalExpr(i) {
        if (i === undefined) {
            return this.getRuleContexts(RelationalExprContext);
        }
        else {
            return this.getRuleContext(i, RelationalExprContext);
        }
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_equalityExpr; }
    // @Override
    enterRule(listener) {
        if (listener.enterEqualityExpr) {
            listener.enterEqualityExpr(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitEqualityExpr) {
            listener.exitEqualityExpr(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitEqualityExpr) {
            return visitor.visitEqualityExpr(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.EqualityExprContext = EqualityExprContext;
class RelationalExprContext extends ParserRuleContext_1.ParserRuleContext {
    additiveExpr(i) {
        if (i === undefined) {
            return this.getRuleContexts(AdditiveExprContext);
        }
        else {
            return this.getRuleContext(i, AdditiveExprContext);
        }
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_relationalExpr; }
    // @Override
    enterRule(listener) {
        if (listener.enterRelationalExpr) {
            listener.enterRelationalExpr(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitRelationalExpr) {
            listener.exitRelationalExpr(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitRelationalExpr) {
            return visitor.visitRelationalExpr(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.RelationalExprContext = RelationalExprContext;
class AdditiveExprContext extends ParserRuleContext_1.ParserRuleContext {
    multiplicativeExpr(i) {
        if (i === undefined) {
            return this.getRuleContexts(MultiplicativeExprContext);
        }
        else {
            return this.getRuleContext(i, MultiplicativeExprContext);
        }
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_additiveExpr; }
    // @Override
    enterRule(listener) {
        if (listener.enterAdditiveExpr) {
            listener.enterAdditiveExpr(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitAdditiveExpr) {
            listener.exitAdditiveExpr(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitAdditiveExpr) {
            return visitor.visitAdditiveExpr(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.AdditiveExprContext = AdditiveExprContext;
class MultiplicativeExprContext extends ParserRuleContext_1.ParserRuleContext {
    unaryExpr(i) {
        if (i === undefined) {
            return this.getRuleContexts(UnaryExprContext);
        }
        else {
            return this.getRuleContext(i, UnaryExprContext);
        }
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_multiplicativeExpr; }
    // @Override
    enterRule(listener) {
        if (listener.enterMultiplicativeExpr) {
            listener.enterMultiplicativeExpr(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitMultiplicativeExpr) {
            listener.exitMultiplicativeExpr(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitMultiplicativeExpr) {
            return visitor.visitMultiplicativeExpr(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.MultiplicativeExprContext = MultiplicativeExprContext;
class UnaryExprContext extends ParserRuleContext_1.ParserRuleContext {
    unaryExpr() {
        return this.tryGetRuleContext(0, UnaryExprContext);
    }
    primaryExpr() {
        return this.tryGetRuleContext(0, PrimaryExprContext);
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_unaryExpr; }
    // @Override
    enterRule(listener) {
        if (listener.enterUnaryExpr) {
            listener.enterUnaryExpr(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitUnaryExpr) {
            listener.exitUnaryExpr(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitUnaryExpr) {
            return visitor.visitUnaryExpr(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.UnaryExprContext = UnaryExprContext;
class PrimaryExprContext extends ParserRuleContext_1.ParserRuleContext {
    literalExpr() {
        return this.tryGetRuleContext(0, LiteralExprContext);
    }
    leftHandSide() {
        return this.tryGetRuleContext(0, LeftHandSideContext);
    }
    expression() {
        return this.tryGetRuleContext(0, ExpressionContext);
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_primaryExpr; }
    // @Override
    enterRule(listener) {
        if (listener.enterPrimaryExpr) {
            listener.enterPrimaryExpr(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitPrimaryExpr) {
            listener.exitPrimaryExpr(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitPrimaryExpr) {
            return visitor.visitPrimaryExpr(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.PrimaryExprContext = PrimaryExprContext;
class LiteralExprContext extends ParserRuleContext_1.ParserRuleContext {
    Literal() { return this.tryGetToken(CompiscriptParser.Literal, 0); }
    arrayLiteral() {
        return this.tryGetRuleContext(0, ArrayLiteralContext);
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_literalExpr; }
    // @Override
    enterRule(listener) {
        if (listener.enterLiteralExpr) {
            listener.enterLiteralExpr(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitLiteralExpr) {
            listener.exitLiteralExpr(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitLiteralExpr) {
            return visitor.visitLiteralExpr(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.LiteralExprContext = LiteralExprContext;
class LeftHandSideContext extends ParserRuleContext_1.ParserRuleContext {
    primaryAtom() {
        return this.getRuleContext(0, PrimaryAtomContext);
    }
    suffixOp(i) {
        if (i === undefined) {
            return this.getRuleContexts(SuffixOpContext);
        }
        else {
            return this.getRuleContext(i, SuffixOpContext);
        }
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_leftHandSide; }
    // @Override
    enterRule(listener) {
        if (listener.enterLeftHandSide) {
            listener.enterLeftHandSide(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitLeftHandSide) {
            listener.exitLeftHandSide(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitLeftHandSide) {
            return visitor.visitLeftHandSide(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.LeftHandSideContext = LeftHandSideContext;
class PrimaryAtomContext extends ParserRuleContext_1.ParserRuleContext {
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_primaryAtom; }
    copyFrom(ctx) {
        super.copyFrom(ctx);
    }
}
exports.PrimaryAtomContext = PrimaryAtomContext;
class IdentifierExprContext extends PrimaryAtomContext {
    Identifier() { return this.getToken(CompiscriptParser.Identifier, 0); }
    constructor(ctx) {
        super(ctx.parent, ctx.invokingState);
        this.copyFrom(ctx);
    }
    // @Override
    enterRule(listener) {
        if (listener.enterIdentifierExpr) {
            listener.enterIdentifierExpr(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitIdentifierExpr) {
            listener.exitIdentifierExpr(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitIdentifierExpr) {
            return visitor.visitIdentifierExpr(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.IdentifierExprContext = IdentifierExprContext;
class NewExprContext extends PrimaryAtomContext {
    Identifier() { return this.getToken(CompiscriptParser.Identifier, 0); }
    arguments() {
        return this.tryGetRuleContext(0, ArgumentsContext);
    }
    constructor(ctx) {
        super(ctx.parent, ctx.invokingState);
        this.copyFrom(ctx);
    }
    // @Override
    enterRule(listener) {
        if (listener.enterNewExpr) {
            listener.enterNewExpr(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitNewExpr) {
            listener.exitNewExpr(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitNewExpr) {
            return visitor.visitNewExpr(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.NewExprContext = NewExprContext;
class ThisExprContext extends PrimaryAtomContext {
    constructor(ctx) {
        super(ctx.parent, ctx.invokingState);
        this.copyFrom(ctx);
    }
    // @Override
    enterRule(listener) {
        if (listener.enterThisExpr) {
            listener.enterThisExpr(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitThisExpr) {
            listener.exitThisExpr(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitThisExpr) {
            return visitor.visitThisExpr(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.ThisExprContext = ThisExprContext;
class SuffixOpContext extends ParserRuleContext_1.ParserRuleContext {
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_suffixOp; }
    copyFrom(ctx) {
        super.copyFrom(ctx);
    }
}
exports.SuffixOpContext = SuffixOpContext;
class CallExprContext extends SuffixOpContext {
    arguments() {
        return this.tryGetRuleContext(0, ArgumentsContext);
    }
    constructor(ctx) {
        super(ctx.parent, ctx.invokingState);
        this.copyFrom(ctx);
    }
    // @Override
    enterRule(listener) {
        if (listener.enterCallExpr) {
            listener.enterCallExpr(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitCallExpr) {
            listener.exitCallExpr(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitCallExpr) {
            return visitor.visitCallExpr(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.CallExprContext = CallExprContext;
class IndexExprContext extends SuffixOpContext {
    expression() {
        return this.getRuleContext(0, ExpressionContext);
    }
    constructor(ctx) {
        super(ctx.parent, ctx.invokingState);
        this.copyFrom(ctx);
    }
    // @Override
    enterRule(listener) {
        if (listener.enterIndexExpr) {
            listener.enterIndexExpr(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitIndexExpr) {
            listener.exitIndexExpr(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitIndexExpr) {
            return visitor.visitIndexExpr(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.IndexExprContext = IndexExprContext;
class PropertyAccessExprContext extends SuffixOpContext {
    Identifier() { return this.getToken(CompiscriptParser.Identifier, 0); }
    constructor(ctx) {
        super(ctx.parent, ctx.invokingState);
        this.copyFrom(ctx);
    }
    // @Override
    enterRule(listener) {
        if (listener.enterPropertyAccessExpr) {
            listener.enterPropertyAccessExpr(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitPropertyAccessExpr) {
            listener.exitPropertyAccessExpr(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitPropertyAccessExpr) {
            return visitor.visitPropertyAccessExpr(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.PropertyAccessExprContext = PropertyAccessExprContext;
class ArgumentsContext extends ParserRuleContext_1.ParserRuleContext {
    expression(i) {
        if (i === undefined) {
            return this.getRuleContexts(ExpressionContext);
        }
        else {
            return this.getRuleContext(i, ExpressionContext);
        }
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_arguments; }
    // @Override
    enterRule(listener) {
        if (listener.enterArguments) {
            listener.enterArguments(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitArguments) {
            listener.exitArguments(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitArguments) {
            return visitor.visitArguments(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.ArgumentsContext = ArgumentsContext;
class ArrayLiteralContext extends ParserRuleContext_1.ParserRuleContext {
    expression(i) {
        if (i === undefined) {
            return this.getRuleContexts(ExpressionContext);
        }
        else {
            return this.getRuleContext(i, ExpressionContext);
        }
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_arrayLiteral; }
    // @Override
    enterRule(listener) {
        if (listener.enterArrayLiteral) {
            listener.enterArrayLiteral(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitArrayLiteral) {
            listener.exitArrayLiteral(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitArrayLiteral) {
            return visitor.visitArrayLiteral(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.ArrayLiteralContext = ArrayLiteralContext;
class TypeContext extends ParserRuleContext_1.ParserRuleContext {
    baseType() {
        return this.getRuleContext(0, BaseTypeContext);
    }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_type; }
    // @Override
    enterRule(listener) {
        if (listener.enterType) {
            listener.enterType(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitType) {
            listener.exitType(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitType) {
            return visitor.visitType(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.TypeContext = TypeContext;
class BaseTypeContext extends ParserRuleContext_1.ParserRuleContext {
    Identifier() { return this.getToken(CompiscriptParser.Identifier, 0); }
    constructor(parent, invokingState) {
        super(parent, invokingState);
    }
    // @Override
    get ruleIndex() { return CompiscriptParser.RULE_baseType; }
    // @Override
    enterRule(listener) {
        if (listener.enterBaseType) {
            listener.enterBaseType(this);
        }
    }
    // @Override
    exitRule(listener) {
        if (listener.exitBaseType) {
            listener.exitBaseType(this);
        }
    }
    // @Override
    accept(visitor) {
        if (visitor.visitBaseType) {
            return visitor.visitBaseType(this);
        }
        else {
            return visitor.visitChildren(this);
        }
    }
}
exports.BaseTypeContext = BaseTypeContext;
//# sourceMappingURL=CompiscriptParser.js.map