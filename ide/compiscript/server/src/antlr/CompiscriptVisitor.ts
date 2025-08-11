// Generated from Compiscript.g4 by ANTLR 4.9.0-SNAPSHOT


import { ParseTreeVisitor } from "antlr4ts/tree/ParseTreeVisitor";

import { AssignExprContext } from "./CompiscriptParser";
import { PropertyAssignExprContext } from "./CompiscriptParser";
import { ExprNoAssignContext } from "./CompiscriptParser";
import { TernaryExprContext } from "./CompiscriptParser";
import { CallExprContext } from "./CompiscriptParser";
import { IndexExprContext } from "./CompiscriptParser";
import { PropertyAccessExprContext } from "./CompiscriptParser";
import { IdentifierExprContext } from "./CompiscriptParser";
import { NewExprContext } from "./CompiscriptParser";
import { ThisExprContext } from "./CompiscriptParser";
import { ProgramContext } from "./CompiscriptParser";
import { StatementContext } from "./CompiscriptParser";
import { BlockContext } from "./CompiscriptParser";
import { VariableDeclarationContext } from "./CompiscriptParser";
import { ConstantDeclarationContext } from "./CompiscriptParser";
import { TypeAnnotationContext } from "./CompiscriptParser";
import { InitializerContext } from "./CompiscriptParser";
import { AssignmentContext } from "./CompiscriptParser";
import { ExpressionStatementContext } from "./CompiscriptParser";
import { PrintStatementContext } from "./CompiscriptParser";
import { IfStatementContext } from "./CompiscriptParser";
import { WhileStatementContext } from "./CompiscriptParser";
import { DoWhileStatementContext } from "./CompiscriptParser";
import { ForStatementContext } from "./CompiscriptParser";
import { ForeachStatementContext } from "./CompiscriptParser";
import { BreakStatementContext } from "./CompiscriptParser";
import { ContinueStatementContext } from "./CompiscriptParser";
import { ReturnStatementContext } from "./CompiscriptParser";
import { TryCatchStatementContext } from "./CompiscriptParser";
import { SwitchStatementContext } from "./CompiscriptParser";
import { SwitchCaseContext } from "./CompiscriptParser";
import { DefaultCaseContext } from "./CompiscriptParser";
import { FunctionDeclarationContext } from "./CompiscriptParser";
import { ParametersContext } from "./CompiscriptParser";
import { ParameterContext } from "./CompiscriptParser";
import { ClassDeclarationContext } from "./CompiscriptParser";
import { ClassMemberContext } from "./CompiscriptParser";
import { ExpressionContext } from "./CompiscriptParser";
import { AssignmentExprContext } from "./CompiscriptParser";
import { ConditionalExprContext } from "./CompiscriptParser";
import { LogicalOrExprContext } from "./CompiscriptParser";
import { LogicalAndExprContext } from "./CompiscriptParser";
import { EqualityExprContext } from "./CompiscriptParser";
import { RelationalExprContext } from "./CompiscriptParser";
import { AdditiveExprContext } from "./CompiscriptParser";
import { MultiplicativeExprContext } from "./CompiscriptParser";
import { UnaryExprContext } from "./CompiscriptParser";
import { PrimaryExprContext } from "./CompiscriptParser";
import { LiteralExprContext } from "./CompiscriptParser";
import { LeftHandSideContext } from "./CompiscriptParser";
import { PrimaryAtomContext } from "./CompiscriptParser";
import { SuffixOpContext } from "./CompiscriptParser";
import { ArgumentsContext } from "./CompiscriptParser";
import { ArrayLiteralContext } from "./CompiscriptParser";
import { TypeContext } from "./CompiscriptParser";
import { BaseTypeContext } from "./CompiscriptParser";


/**
 * This interface defines a complete generic visitor for a parse tree produced
 * by `CompiscriptParser`.
 *
 * @param <Result> The return type of the visit operation. Use `void` for
 * operations with no return type.
 */
export interface CompiscriptVisitor<Result> extends ParseTreeVisitor<Result> {
	/**
	 * Visit a parse tree produced by the `AssignExpr`
	 * labeled alternative in `CompiscriptParser.assignmentExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitAssignExpr?: (ctx: AssignExprContext) => Result;

	/**
	 * Visit a parse tree produced by the `PropertyAssignExpr`
	 * labeled alternative in `CompiscriptParser.assignmentExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitPropertyAssignExpr?: (ctx: PropertyAssignExprContext) => Result;

	/**
	 * Visit a parse tree produced by the `ExprNoAssign`
	 * labeled alternative in `CompiscriptParser.assignmentExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitExprNoAssign?: (ctx: ExprNoAssignContext) => Result;

	/**
	 * Visit a parse tree produced by the `TernaryExpr`
	 * labeled alternative in `CompiscriptParser.conditionalExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitTernaryExpr?: (ctx: TernaryExprContext) => Result;

	/**
	 * Visit a parse tree produced by the `CallExpr`
	 * labeled alternative in `CompiscriptParser.suffixOp`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitCallExpr?: (ctx: CallExprContext) => Result;

	/**
	 * Visit a parse tree produced by the `IndexExpr`
	 * labeled alternative in `CompiscriptParser.suffixOp`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitIndexExpr?: (ctx: IndexExprContext) => Result;

	/**
	 * Visit a parse tree produced by the `PropertyAccessExpr`
	 * labeled alternative in `CompiscriptParser.suffixOp`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitPropertyAccessExpr?: (ctx: PropertyAccessExprContext) => Result;

	/**
	 * Visit a parse tree produced by the `IdentifierExpr`
	 * labeled alternative in `CompiscriptParser.primaryAtom`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitIdentifierExpr?: (ctx: IdentifierExprContext) => Result;

	/**
	 * Visit a parse tree produced by the `NewExpr`
	 * labeled alternative in `CompiscriptParser.primaryAtom`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitNewExpr?: (ctx: NewExprContext) => Result;

	/**
	 * Visit a parse tree produced by the `ThisExpr`
	 * labeled alternative in `CompiscriptParser.primaryAtom`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitThisExpr?: (ctx: ThisExprContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.program`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitProgram?: (ctx: ProgramContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.statement`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitStatement?: (ctx: StatementContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.block`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitBlock?: (ctx: BlockContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.variableDeclaration`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitVariableDeclaration?: (ctx: VariableDeclarationContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.constantDeclaration`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitConstantDeclaration?: (ctx: ConstantDeclarationContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.typeAnnotation`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitTypeAnnotation?: (ctx: TypeAnnotationContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.initializer`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitInitializer?: (ctx: InitializerContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.assignment`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitAssignment?: (ctx: AssignmentContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.expressionStatement`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitExpressionStatement?: (ctx: ExpressionStatementContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.printStatement`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitPrintStatement?: (ctx: PrintStatementContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.ifStatement`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitIfStatement?: (ctx: IfStatementContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.whileStatement`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitWhileStatement?: (ctx: WhileStatementContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.doWhileStatement`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitDoWhileStatement?: (ctx: DoWhileStatementContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.forStatement`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitForStatement?: (ctx: ForStatementContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.foreachStatement`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitForeachStatement?: (ctx: ForeachStatementContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.breakStatement`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitBreakStatement?: (ctx: BreakStatementContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.continueStatement`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitContinueStatement?: (ctx: ContinueStatementContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.returnStatement`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitReturnStatement?: (ctx: ReturnStatementContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.tryCatchStatement`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitTryCatchStatement?: (ctx: TryCatchStatementContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.switchStatement`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitSwitchStatement?: (ctx: SwitchStatementContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.switchCase`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitSwitchCase?: (ctx: SwitchCaseContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.defaultCase`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitDefaultCase?: (ctx: DefaultCaseContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.functionDeclaration`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitFunctionDeclaration?: (ctx: FunctionDeclarationContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.parameters`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitParameters?: (ctx: ParametersContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.parameter`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitParameter?: (ctx: ParameterContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.classDeclaration`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitClassDeclaration?: (ctx: ClassDeclarationContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.classMember`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitClassMember?: (ctx: ClassMemberContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.expression`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitExpression?: (ctx: ExpressionContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.assignmentExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitAssignmentExpr?: (ctx: AssignmentExprContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.conditionalExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitConditionalExpr?: (ctx: ConditionalExprContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.logicalOrExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitLogicalOrExpr?: (ctx: LogicalOrExprContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.logicalAndExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitLogicalAndExpr?: (ctx: LogicalAndExprContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.equalityExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitEqualityExpr?: (ctx: EqualityExprContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.relationalExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitRelationalExpr?: (ctx: RelationalExprContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.additiveExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitAdditiveExpr?: (ctx: AdditiveExprContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.multiplicativeExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitMultiplicativeExpr?: (ctx: MultiplicativeExprContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.unaryExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitUnaryExpr?: (ctx: UnaryExprContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.primaryExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitPrimaryExpr?: (ctx: PrimaryExprContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.literalExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitLiteralExpr?: (ctx: LiteralExprContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.leftHandSide`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitLeftHandSide?: (ctx: LeftHandSideContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.primaryAtom`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitPrimaryAtom?: (ctx: PrimaryAtomContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.suffixOp`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitSuffixOp?: (ctx: SuffixOpContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.arguments`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitArguments?: (ctx: ArgumentsContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.arrayLiteral`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitArrayLiteral?: (ctx: ArrayLiteralContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.type`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitType?: (ctx: TypeContext) => Result;

	/**
	 * Visit a parse tree produced by `CompiscriptParser.baseType`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitBaseType?: (ctx: BaseTypeContext) => Result;
}

