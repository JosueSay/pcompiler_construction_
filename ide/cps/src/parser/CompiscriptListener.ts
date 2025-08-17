// Generated from src/grammar/Compiscript.g4 by ANTLR 4.9.0-SNAPSHOT


import { ParseTreeListener } from "antlr4ts/tree/ParseTreeListener";

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
 * This interface defines a complete listener for a parse tree produced by
 * `CompiscriptParser`.
 */
export interface CompiscriptListener extends ParseTreeListener {
	/**
	 * Enter a parse tree produced by the `AssignExpr`
	 * labeled alternative in `CompiscriptParser.assignmentExpr`.
	 * @param ctx the parse tree
	 */
	enterAssignExpr?: (ctx: AssignExprContext) => void;
	/**
	 * Exit a parse tree produced by the `AssignExpr`
	 * labeled alternative in `CompiscriptParser.assignmentExpr`.
	 * @param ctx the parse tree
	 */
	exitAssignExpr?: (ctx: AssignExprContext) => void;

	/**
	 * Enter a parse tree produced by the `PropertyAssignExpr`
	 * labeled alternative in `CompiscriptParser.assignmentExpr`.
	 * @param ctx the parse tree
	 */
	enterPropertyAssignExpr?: (ctx: PropertyAssignExprContext) => void;
	/**
	 * Exit a parse tree produced by the `PropertyAssignExpr`
	 * labeled alternative in `CompiscriptParser.assignmentExpr`.
	 * @param ctx the parse tree
	 */
	exitPropertyAssignExpr?: (ctx: PropertyAssignExprContext) => void;

	/**
	 * Enter a parse tree produced by the `ExprNoAssign`
	 * labeled alternative in `CompiscriptParser.assignmentExpr`.
	 * @param ctx the parse tree
	 */
	enterExprNoAssign?: (ctx: ExprNoAssignContext) => void;
	/**
	 * Exit a parse tree produced by the `ExprNoAssign`
	 * labeled alternative in `CompiscriptParser.assignmentExpr`.
	 * @param ctx the parse tree
	 */
	exitExprNoAssign?: (ctx: ExprNoAssignContext) => void;

	/**
	 * Enter a parse tree produced by the `TernaryExpr`
	 * labeled alternative in `CompiscriptParser.conditionalExpr`.
	 * @param ctx the parse tree
	 */
	enterTernaryExpr?: (ctx: TernaryExprContext) => void;
	/**
	 * Exit a parse tree produced by the `TernaryExpr`
	 * labeled alternative in `CompiscriptParser.conditionalExpr`.
	 * @param ctx the parse tree
	 */
	exitTernaryExpr?: (ctx: TernaryExprContext) => void;

	/**
	 * Enter a parse tree produced by the `CallExpr`
	 * labeled alternative in `CompiscriptParser.suffixOp`.
	 * @param ctx the parse tree
	 */
	enterCallExpr?: (ctx: CallExprContext) => void;
	/**
	 * Exit a parse tree produced by the `CallExpr`
	 * labeled alternative in `CompiscriptParser.suffixOp`.
	 * @param ctx the parse tree
	 */
	exitCallExpr?: (ctx: CallExprContext) => void;

	/**
	 * Enter a parse tree produced by the `IndexExpr`
	 * labeled alternative in `CompiscriptParser.suffixOp`.
	 * @param ctx the parse tree
	 */
	enterIndexExpr?: (ctx: IndexExprContext) => void;
	/**
	 * Exit a parse tree produced by the `IndexExpr`
	 * labeled alternative in `CompiscriptParser.suffixOp`.
	 * @param ctx the parse tree
	 */
	exitIndexExpr?: (ctx: IndexExprContext) => void;

	/**
	 * Enter a parse tree produced by the `PropertyAccessExpr`
	 * labeled alternative in `CompiscriptParser.suffixOp`.
	 * @param ctx the parse tree
	 */
	enterPropertyAccessExpr?: (ctx: PropertyAccessExprContext) => void;
	/**
	 * Exit a parse tree produced by the `PropertyAccessExpr`
	 * labeled alternative in `CompiscriptParser.suffixOp`.
	 * @param ctx the parse tree
	 */
	exitPropertyAccessExpr?: (ctx: PropertyAccessExprContext) => void;

	/**
	 * Enter a parse tree produced by the `IdentifierExpr`
	 * labeled alternative in `CompiscriptParser.primaryAtom`.
	 * @param ctx the parse tree
	 */
	enterIdentifierExpr?: (ctx: IdentifierExprContext) => void;
	/**
	 * Exit a parse tree produced by the `IdentifierExpr`
	 * labeled alternative in `CompiscriptParser.primaryAtom`.
	 * @param ctx the parse tree
	 */
	exitIdentifierExpr?: (ctx: IdentifierExprContext) => void;

	/**
	 * Enter a parse tree produced by the `NewExpr`
	 * labeled alternative in `CompiscriptParser.primaryAtom`.
	 * @param ctx the parse tree
	 */
	enterNewExpr?: (ctx: NewExprContext) => void;
	/**
	 * Exit a parse tree produced by the `NewExpr`
	 * labeled alternative in `CompiscriptParser.primaryAtom`.
	 * @param ctx the parse tree
	 */
	exitNewExpr?: (ctx: NewExprContext) => void;

	/**
	 * Enter a parse tree produced by the `ThisExpr`
	 * labeled alternative in `CompiscriptParser.primaryAtom`.
	 * @param ctx the parse tree
	 */
	enterThisExpr?: (ctx: ThisExprContext) => void;
	/**
	 * Exit a parse tree produced by the `ThisExpr`
	 * labeled alternative in `CompiscriptParser.primaryAtom`.
	 * @param ctx the parse tree
	 */
	exitThisExpr?: (ctx: ThisExprContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.program`.
	 * @param ctx the parse tree
	 */
	enterProgram?: (ctx: ProgramContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.program`.
	 * @param ctx the parse tree
	 */
	exitProgram?: (ctx: ProgramContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.statement`.
	 * @param ctx the parse tree
	 */
	enterStatement?: (ctx: StatementContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.statement`.
	 * @param ctx the parse tree
	 */
	exitStatement?: (ctx: StatementContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.block`.
	 * @param ctx the parse tree
	 */
	enterBlock?: (ctx: BlockContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.block`.
	 * @param ctx the parse tree
	 */
	exitBlock?: (ctx: BlockContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.variableDeclaration`.
	 * @param ctx the parse tree
	 */
	enterVariableDeclaration?: (ctx: VariableDeclarationContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.variableDeclaration`.
	 * @param ctx the parse tree
	 */
	exitVariableDeclaration?: (ctx: VariableDeclarationContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.constantDeclaration`.
	 * @param ctx the parse tree
	 */
	enterConstantDeclaration?: (ctx: ConstantDeclarationContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.constantDeclaration`.
	 * @param ctx the parse tree
	 */
	exitConstantDeclaration?: (ctx: ConstantDeclarationContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.typeAnnotation`.
	 * @param ctx the parse tree
	 */
	enterTypeAnnotation?: (ctx: TypeAnnotationContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.typeAnnotation`.
	 * @param ctx the parse tree
	 */
	exitTypeAnnotation?: (ctx: TypeAnnotationContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.initializer`.
	 * @param ctx the parse tree
	 */
	enterInitializer?: (ctx: InitializerContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.initializer`.
	 * @param ctx the parse tree
	 */
	exitInitializer?: (ctx: InitializerContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.assignment`.
	 * @param ctx the parse tree
	 */
	enterAssignment?: (ctx: AssignmentContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.assignment`.
	 * @param ctx the parse tree
	 */
	exitAssignment?: (ctx: AssignmentContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.expressionStatement`.
	 * @param ctx the parse tree
	 */
	enterExpressionStatement?: (ctx: ExpressionStatementContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.expressionStatement`.
	 * @param ctx the parse tree
	 */
	exitExpressionStatement?: (ctx: ExpressionStatementContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.printStatement`.
	 * @param ctx the parse tree
	 */
	enterPrintStatement?: (ctx: PrintStatementContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.printStatement`.
	 * @param ctx the parse tree
	 */
	exitPrintStatement?: (ctx: PrintStatementContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.ifStatement`.
	 * @param ctx the parse tree
	 */
	enterIfStatement?: (ctx: IfStatementContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.ifStatement`.
	 * @param ctx the parse tree
	 */
	exitIfStatement?: (ctx: IfStatementContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.whileStatement`.
	 * @param ctx the parse tree
	 */
	enterWhileStatement?: (ctx: WhileStatementContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.whileStatement`.
	 * @param ctx the parse tree
	 */
	exitWhileStatement?: (ctx: WhileStatementContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.doWhileStatement`.
	 * @param ctx the parse tree
	 */
	enterDoWhileStatement?: (ctx: DoWhileStatementContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.doWhileStatement`.
	 * @param ctx the parse tree
	 */
	exitDoWhileStatement?: (ctx: DoWhileStatementContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.forStatement`.
	 * @param ctx the parse tree
	 */
	enterForStatement?: (ctx: ForStatementContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.forStatement`.
	 * @param ctx the parse tree
	 */
	exitForStatement?: (ctx: ForStatementContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.foreachStatement`.
	 * @param ctx the parse tree
	 */
	enterForeachStatement?: (ctx: ForeachStatementContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.foreachStatement`.
	 * @param ctx the parse tree
	 */
	exitForeachStatement?: (ctx: ForeachStatementContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.breakStatement`.
	 * @param ctx the parse tree
	 */
	enterBreakStatement?: (ctx: BreakStatementContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.breakStatement`.
	 * @param ctx the parse tree
	 */
	exitBreakStatement?: (ctx: BreakStatementContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.continueStatement`.
	 * @param ctx the parse tree
	 */
	enterContinueStatement?: (ctx: ContinueStatementContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.continueStatement`.
	 * @param ctx the parse tree
	 */
	exitContinueStatement?: (ctx: ContinueStatementContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.returnStatement`.
	 * @param ctx the parse tree
	 */
	enterReturnStatement?: (ctx: ReturnStatementContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.returnStatement`.
	 * @param ctx the parse tree
	 */
	exitReturnStatement?: (ctx: ReturnStatementContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.tryCatchStatement`.
	 * @param ctx the parse tree
	 */
	enterTryCatchStatement?: (ctx: TryCatchStatementContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.tryCatchStatement`.
	 * @param ctx the parse tree
	 */
	exitTryCatchStatement?: (ctx: TryCatchStatementContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.switchStatement`.
	 * @param ctx the parse tree
	 */
	enterSwitchStatement?: (ctx: SwitchStatementContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.switchStatement`.
	 * @param ctx the parse tree
	 */
	exitSwitchStatement?: (ctx: SwitchStatementContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.switchCase`.
	 * @param ctx the parse tree
	 */
	enterSwitchCase?: (ctx: SwitchCaseContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.switchCase`.
	 * @param ctx the parse tree
	 */
	exitSwitchCase?: (ctx: SwitchCaseContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.defaultCase`.
	 * @param ctx the parse tree
	 */
	enterDefaultCase?: (ctx: DefaultCaseContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.defaultCase`.
	 * @param ctx the parse tree
	 */
	exitDefaultCase?: (ctx: DefaultCaseContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.functionDeclaration`.
	 * @param ctx the parse tree
	 */
	enterFunctionDeclaration?: (ctx: FunctionDeclarationContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.functionDeclaration`.
	 * @param ctx the parse tree
	 */
	exitFunctionDeclaration?: (ctx: FunctionDeclarationContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.parameters`.
	 * @param ctx the parse tree
	 */
	enterParameters?: (ctx: ParametersContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.parameters`.
	 * @param ctx the parse tree
	 */
	exitParameters?: (ctx: ParametersContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.parameter`.
	 * @param ctx the parse tree
	 */
	enterParameter?: (ctx: ParameterContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.parameter`.
	 * @param ctx the parse tree
	 */
	exitParameter?: (ctx: ParameterContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.classDeclaration`.
	 * @param ctx the parse tree
	 */
	enterClassDeclaration?: (ctx: ClassDeclarationContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.classDeclaration`.
	 * @param ctx the parse tree
	 */
	exitClassDeclaration?: (ctx: ClassDeclarationContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.classMember`.
	 * @param ctx the parse tree
	 */
	enterClassMember?: (ctx: ClassMemberContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.classMember`.
	 * @param ctx the parse tree
	 */
	exitClassMember?: (ctx: ClassMemberContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.expression`.
	 * @param ctx the parse tree
	 */
	enterExpression?: (ctx: ExpressionContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.expression`.
	 * @param ctx the parse tree
	 */
	exitExpression?: (ctx: ExpressionContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.assignmentExpr`.
	 * @param ctx the parse tree
	 */
	enterAssignmentExpr?: (ctx: AssignmentExprContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.assignmentExpr`.
	 * @param ctx the parse tree
	 */
	exitAssignmentExpr?: (ctx: AssignmentExprContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.conditionalExpr`.
	 * @param ctx the parse tree
	 */
	enterConditionalExpr?: (ctx: ConditionalExprContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.conditionalExpr`.
	 * @param ctx the parse tree
	 */
	exitConditionalExpr?: (ctx: ConditionalExprContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.logicalOrExpr`.
	 * @param ctx the parse tree
	 */
	enterLogicalOrExpr?: (ctx: LogicalOrExprContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.logicalOrExpr`.
	 * @param ctx the parse tree
	 */
	exitLogicalOrExpr?: (ctx: LogicalOrExprContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.logicalAndExpr`.
	 * @param ctx the parse tree
	 */
	enterLogicalAndExpr?: (ctx: LogicalAndExprContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.logicalAndExpr`.
	 * @param ctx the parse tree
	 */
	exitLogicalAndExpr?: (ctx: LogicalAndExprContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.equalityExpr`.
	 * @param ctx the parse tree
	 */
	enterEqualityExpr?: (ctx: EqualityExprContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.equalityExpr`.
	 * @param ctx the parse tree
	 */
	exitEqualityExpr?: (ctx: EqualityExprContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.relationalExpr`.
	 * @param ctx the parse tree
	 */
	enterRelationalExpr?: (ctx: RelationalExprContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.relationalExpr`.
	 * @param ctx the parse tree
	 */
	exitRelationalExpr?: (ctx: RelationalExprContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.additiveExpr`.
	 * @param ctx the parse tree
	 */
	enterAdditiveExpr?: (ctx: AdditiveExprContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.additiveExpr`.
	 * @param ctx the parse tree
	 */
	exitAdditiveExpr?: (ctx: AdditiveExprContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.multiplicativeExpr`.
	 * @param ctx the parse tree
	 */
	enterMultiplicativeExpr?: (ctx: MultiplicativeExprContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.multiplicativeExpr`.
	 * @param ctx the parse tree
	 */
	exitMultiplicativeExpr?: (ctx: MultiplicativeExprContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.unaryExpr`.
	 * @param ctx the parse tree
	 */
	enterUnaryExpr?: (ctx: UnaryExprContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.unaryExpr`.
	 * @param ctx the parse tree
	 */
	exitUnaryExpr?: (ctx: UnaryExprContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.primaryExpr`.
	 * @param ctx the parse tree
	 */
	enterPrimaryExpr?: (ctx: PrimaryExprContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.primaryExpr`.
	 * @param ctx the parse tree
	 */
	exitPrimaryExpr?: (ctx: PrimaryExprContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.literalExpr`.
	 * @param ctx the parse tree
	 */
	enterLiteralExpr?: (ctx: LiteralExprContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.literalExpr`.
	 * @param ctx the parse tree
	 */
	exitLiteralExpr?: (ctx: LiteralExprContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.leftHandSide`.
	 * @param ctx the parse tree
	 */
	enterLeftHandSide?: (ctx: LeftHandSideContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.leftHandSide`.
	 * @param ctx the parse tree
	 */
	exitLeftHandSide?: (ctx: LeftHandSideContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.primaryAtom`.
	 * @param ctx the parse tree
	 */
	enterPrimaryAtom?: (ctx: PrimaryAtomContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.primaryAtom`.
	 * @param ctx the parse tree
	 */
	exitPrimaryAtom?: (ctx: PrimaryAtomContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.suffixOp`.
	 * @param ctx the parse tree
	 */
	enterSuffixOp?: (ctx: SuffixOpContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.suffixOp`.
	 * @param ctx the parse tree
	 */
	exitSuffixOp?: (ctx: SuffixOpContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.arguments`.
	 * @param ctx the parse tree
	 */
	enterArguments?: (ctx: ArgumentsContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.arguments`.
	 * @param ctx the parse tree
	 */
	exitArguments?: (ctx: ArgumentsContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.arrayLiteral`.
	 * @param ctx the parse tree
	 */
	enterArrayLiteral?: (ctx: ArrayLiteralContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.arrayLiteral`.
	 * @param ctx the parse tree
	 */
	exitArrayLiteral?: (ctx: ArrayLiteralContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.type`.
	 * @param ctx the parse tree
	 */
	enterType?: (ctx: TypeContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.type`.
	 * @param ctx the parse tree
	 */
	exitType?: (ctx: TypeContext) => void;

	/**
	 * Enter a parse tree produced by `CompiscriptParser.baseType`.
	 * @param ctx the parse tree
	 */
	enterBaseType?: (ctx: BaseTypeContext) => void;
	/**
	 * Exit a parse tree produced by `CompiscriptParser.baseType`.
	 * @param ctx the parse tree
	 */
	exitBaseType?: (ctx: BaseTypeContext) => void;
}

