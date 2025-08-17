"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CpsEvalVisitor = void 0;
const tree_1 = require("antlr4ts/tree");
const CompiscriptParser_1 = require("../parser/CompiscriptParser");
class RuntimeError extends Error {
}
class ReturnSignal {
    constructor(value) {
        this.value = value;
    }
}
class Environment {
    constructor(parent) {
        this.parent = parent;
        this.table = new Map();
    }
    define(name, value, constant = false) {
        if (this.table.has(name))
            throw new RuntimeError(`'${name}' already declared`);
        this.table.set(name, { value, constant });
    }
    assign(name, value) {
        const env = this.resolve(name);
        if (!env)
            throw new RuntimeError(`Undefined '${name}'`);
        const r = env.table.get(name);
        if (r.constant)
            throw new RuntimeError(`Cannot assign to const '${name}'`);
        r.value = value;
    }
    get(name) {
        const env = this.resolve(name);
        if (!env)
            throw new RuntimeError(`Undefined '${name}'`);
        return env.table.get(name).value;
    }
    resolve(name) {
        if (this.table.has(name))
            return this;
        return this.parent?.resolve(name);
    }
}
class FunctionValue {
    constructor(params, body, closure, native) {
        this.params = params;
        this.body = body;
        this.closure = closure;
        this.native = native;
    }
    call(args, visitor) {
        if (this.native)
            return this.native(args);
        const local = new Environment(this.closure);
        for (let i = 0; i < this.params.length; i++) {
            local.define(this.params[i], args[i] ?? null, false);
        }
        try {
            return visitor.withEnv(local, () => {
                visitor.visit(this.body);
                return null;
            });
        }
        catch (e) {
            if (e instanceof ReturnSignal)
                return e.value;
            throw e;
        }
    }
}
// ================= Visitor =================
class CpsEvalVisitor extends tree_1.AbstractParseTreeVisitor {
    constructor(globalEnv) {
        super();
        this.env = globalEnv ?? new Environment();
        if (!globalEnv) {
            // stdlib
            this.env.define('print', new FunctionValue(['x'], {}, this.env, (args) => {
                // eslint-disable-next-line no-console
                return null;
            }), true);
            this.env.define('len', new FunctionValue(['x'], {}, this.env, (args) => {
                const v = args[0];
                if (Array.isArray(v) || typeof v === 'string')
                    return v.length;
                if (v && typeof v === 'object')
                    return Object.keys(v).length;
                return 0;
            }), true);
        }
    }
    defaultResult() { return null; }
    // ------- env helper -------
    withEnv(next, fn) {
        const prev = this.env;
        this.env = next;
        try {
            return fn();
        }
        finally {
            this.env = prev;
        }
    }
    // ================= Top-Level =================
    visitProgram(ctx) {
        for (const st of ctx.statement())
            this.visit(st);
        return null;
    }
    visitBlock(ctx) {
        const child = new Environment(this.env);
        return this.withEnv(child, () => {
            for (const s of ctx.statement())
                this.visit(s);
            return null;
        });
    }
    // ================= Statements =================
    visitVariableDeclaration(ctx) {
        const name = ctx.Identifier().text;
        const init = ctx.initializer() ? this.visit(ctx.initializer().expression()) : null;
        this.env.define(name, init, false);
        return null;
    }
    visitConstantDeclaration(ctx) {
        const name = ctx.Identifier().text;
        const init = this.visit(ctx.expression());
        this.env.define(name, init, true);
        return null;
    }
    visitAssignment(ctx) {
        if (ctx.Identifier()) {
            const name = ctx.Identifier().text;
            const value = this.visit(ctx.expression(0));
            this.env.assign(name, value);
            return value;
        }
        // property assignment: expr '.' Identifier '=' expr ';'
        const obj = this.visit(ctx.expression(0));
        const prop = ctx.Identifier().text;
        const val = this.visit(ctx.expression(1));
        if (obj && typeof obj === 'object' && !Array.isArray(obj)) {
            obj[prop] = val;
            return val;
        }
        throw new RuntimeError('Left-hand side is not an object');
    }
    visitExpressionStatement(ctx) {
        return this.visit(ctx.expression());
    }
    visitPrintStatement(ctx) {
        const v = this.visit(ctx.expression());
        // eslint-disable-next-line no-console
        return null;
    }
    visitIfStatement(ctx) {
        if (this.truthy(this.visit(ctx.expression()))) {
            this.visit(ctx.block(0));
        }
        else if (ctx.block(1)) {
            this.visit(ctx.block(1));
        }
        return null;
    }
    visitWhileStatement(ctx) {
        while (this.truthy(this.visit(ctx.expression()))) {
            this.visit(ctx.block());
        }
        return null;
    }
    visitDoWhileStatement(ctx) {
        do {
            this.visit(ctx.block());
        } while (this.truthy(this.visit(ctx.expression())));
        return null;
    }
    visitForStatement(ctx) {
        const loopEnv = new Environment(this.env);
        return this.withEnv(loopEnv, () => {
            if (ctx.variableDeclaration())
                this.visit(ctx.variableDeclaration());
            else if (ctx.assignment())
                this.visit(ctx.assignment());
            const cond = ctx.expression(0);
            const inc = ctx.expression(1);
            while (!cond || this.truthy(this.visit(cond))) {
                this.visit(ctx.block());
                if (inc)
                    this.visit(inc);
            }
            return null;
        });
    }
    visitForeachStatement(ctx) {
        const name = ctx.Identifier().text;
        const iterable = this.visit(ctx.expression());
        if (!Array.isArray(iterable))
            throw new RuntimeError('foreach expects an array');
        const loopEnv = new Environment(this.env);
        return this.withEnv(loopEnv, () => {
            for (const it of iterable) {
                loopEnv.resolve(name) ? loopEnv.assign(name, it) : loopEnv.define(name, it, false);
                this.visit(ctx.block());
            }
            return null;
        });
    }
    visitReturnStatement(ctx) {
        const val = ctx.expression() ? this.visit(ctx.expression()) : null;
        throw new ReturnSignal(val);
    }
    // Function declarations
    visitFunctionDeclaration(ctx) {
        const name = ctx.Identifier().text;
        const params = ctx.parameters()
            ? ctx.parameters().parameter().map(p => p.Identifier().text)
            : [];
        const fn = new FunctionValue(params, ctx.block(), this.env);
        this.env.define(name, fn, true);
        return null;
    }
    // ================= Expressions (precedence chain) =================
    visitAssignExpr(ctx) {
        // rhs
        const value = this.visit(ctx.assignmentExpr());
        // simple: id = ...
        const patom = ctx._lhs.primaryAtom();
        if (patom instanceof CompiscriptParser_1.IdentifierExprContext) {
            this.env.assign(patom.Identifier().text, value);
            return value;
        }
        // complex: a.b[0] = ...
        this.assignIntoLeft(ctx._lhs, value);
        return value;
    }
    visitPropertyAssignExpr(ctx) {
        const base = this.evalLeft(ctx._lhs);
        const value = this.visit(ctx.assignmentExpr());
        const prop = ctx.Identifier().text;
        if (base && typeof base === 'object' && !Array.isArray(base)) {
            base[prop] = value;
            return value;
        }
        throw new RuntimeError('Property assignment on non-object');
    }
    visitTernaryExpr(ctx) {
        // Ternary form: logicalOrExpr '?' expression ':' expression
        if (ctx.expression().length === 2) {
            const cond = this.visit(ctx.logicalOrExpr());
            return this.truthy(cond)
                ? this.visit(ctx.expression(0))
                : this.visit(ctx.expression(1));
        }
        // No '? :' → just return the or-expression
        return this.visit(ctx.logicalOrExpr());
    }
    visitLogicalAndExpr(ctx) {
        let acc = this.visit(ctx.equalityExpr(0));
        for (let i = 1; i < ctx.equalityExpr().length; i++) {
            const right = this.visit(ctx.equalityExpr(i));
            if (!this.truthy(acc))
                return false;
            acc = this.truthy(acc) && this.truthy(right);
        }
        return this.truthy(acc);
    }
    visitEqualityExpr(ctx) {
        let v = this.visit(ctx.relationalExpr(0));
        for (let i = 1; i < ctx.relationalExpr().length; i++) {
            const op = ctx.children[2 * i - 1].text;
            const r = this.visit(ctx.relationalExpr(i));
            v = (op === '==') ? this.equals(v, r) : !this.equals(v, r);
        }
        return v;
    }
    visitRelationalExpr(ctx) {
        let v = this.visit(ctx.additiveExpr(0));
        for (let i = 1; i < ctx.additiveExpr().length; i++) {
            const op = ctx.children[2 * i - 1].text;
            const r = this.visit(ctx.additiveExpr(i));
            switch (op) {
                case '<':
                    v = this.num(v) < this.num(r);
                    break;
                case '<=':
                    v = this.num(v) <= this.num(r);
                    break;
                case '>':
                    v = this.num(v) > this.num(r);
                    break;
                case '>=':
                    v = this.num(v) >= this.num(r);
                    break;
            }
        }
        return v;
    }
    visitAdditiveExpr(ctx) {
        let v = this.visit(ctx.multiplicativeExpr(0));
        for (let i = 1; i < ctx.multiplicativeExpr().length; i++) {
            const op = ctx.children[2 * i - 1].text;
            const r = this.visit(ctx.multiplicativeExpr(i));
            if (op === '+') {
                if (typeof v === 'string' || typeof r === 'string')
                    v = String(v) + String(r);
                else
                    v = this.num(v) + this.num(r);
            }
            else {
                v = this.num(v) - this.num(r);
            }
        }
        return v;
    }
    visitMultiplicativeExpr(ctx) {
        let v = this.visit(ctx.unaryExpr(0));
        for (let i = 1; i < ctx.unaryExpr().length; i++) {
            const op = ctx.children[2 * i - 1].text;
            const r = this.visit(ctx.unaryExpr(i));
            switch (op) {
                case '*':
                    v = this.num(v) * this.num(r);
                    break;
                case '/':
                    v = this.num(v) / this.num(r);
                    break;
                case '%':
                    v = this.num(v) % this.num(r);
                    break;
            }
        }
        return v;
    }
    visitUnaryOp(ctx) {
        const kids = ctx.children;
        if (!kids || kids.length === 0)
            return null;
        const op = kids[0].text; // '-' or '!'
        const rhs = ctx.unaryExpr();
        if (!rhs)
            return null;
        const v = this.visit(rhs);
        return op === '!' ? !this.truthy(v) : -this.num(v);
    }
    visitUnaryPrimary(ctx) {
        const prim = ctx.primaryExpr();
        return prim ? this.visit(prim) : null;
    }
    visitPrimaryExpr(ctx) {
        if (ctx.literalExpr())
            return this.visit(ctx.literalExpr());
        if (ctx.leftHandSide())
            return this.evalLeft(ctx.leftHandSide());
        if (ctx.expression())
            return this.visit(ctx.expression()); // (expr)
        return null;
    }
    visitArrayLiteral(ctx) {
        return ctx.expression().map(e => this.visit(e));
    }
    visitLiteralExpr(ctx) {
        const text = ctx.text;
        if (text === 'null')
            return null;
        if (text === 'true')
            return true;
        if (text === 'false')
            return false;
        // handle Literal (Integer or String)
        const lit = ctx.Literal();
        if (lit) {
            const t = lit.text;
            if (/^".*"$/.test(t)) {
                return this.stripQuotes(t);
            }
            return Number(t);
        }
        // handle array literal
        const arr = ctx.arrayLiteral();
        if (arr)
            return this.visit(arr);
        return null; // or throw an error
    }
    // ============ Left-hand side chain ============
    evalLeft(ctx) {
        let base = this.evalPrimaryAtom(ctx.primaryAtom());
        for (const s of ctx.suffixOp()) {
            const first = s.start.text;
            if (first === '(') {
                const argsCtx = s.arguments();
                const args = argsCtx ? argsCtx.expression().map(e => this.visit(e)) : [];
                if (!(base instanceof FunctionValue))
                    throw new RuntimeError('Call on non-function');
                base = base.call(args, this);
            }
            else if (first === '[') {
                const idx = this.visit(s.expression());
                if (Array.isArray(base))
                    base = base[this.num(idx)];
                else if (base && typeof base === 'object')
                    base = base[String(idx)];
                else
                    throw new RuntimeError('Indexing non-indexable');
            }
            else if (first === '.') {
                const name = s.Identifier().text;
                if (base && typeof base === 'object')
                    base = base[name];
                else
                    throw new RuntimeError('Property access on non-object');
            }
        }
        return base;
    }
    evalPrimaryAtom(ctx) {
        if (ctx instanceof CompiscriptParser_1.IdentifierExprContext) {
            return this.env.get(ctx.Identifier().text);
        }
        if (ctx instanceof CompiscriptParser_1.ThisExprContext) {
            return null; // or your bound `this`
        }
        if (ctx instanceof CompiscriptParser_1.NewExprContext) {
            const className = ctx.Identifier().text;
            // TODO: construct instance from className
            return {};
        }
        return null;
    }
    assignIntoLeft(lhs, value) {
        let base = this.evalPrimaryAtom(lhs.primaryAtom());
        const suffixes = lhs.suffixOp();
        for (let i = 0; i < suffixes.length - 1; i++) {
            const s = suffixes[i];
            if (s instanceof CompiscriptParser_1.CallExprContext) {
                throw new RuntimeError('Cannot assign to call result');
            }
            else if (s instanceof CompiscriptParser_1.IndexExprContext) {
                const key = this.visit(s.expression());
                base = Array.isArray(base) ? base[this.num(key)] : base[String(key)];
            }
            else if (s instanceof CompiscriptParser_1.PropertyAccessExprContext) {
                base = base[s.Identifier().text];
            }
            if (base === undefined || base === null)
                throw new RuntimeError('Assign through undefined/null');
        }
        const last = suffixes[suffixes.length - 1];
        if (last instanceof CompiscriptParser_1.IndexExprContext) {
            const key = this.visit(last.expression());
            if (Array.isArray(base))
                base[this.num(key)] = value;
            else
                base[String(key)] = value;
        }
        else if (last instanceof CompiscriptParser_1.PropertyAccessExprContext) {
            base[last.Identifier().text] = value;
        }
        else {
            throw new RuntimeError('Invalid assignment target');
        }
    }
    // ============ Utils ============
    stripQuotes(s) { return s.slice(1, -1); }
    truthy(v) { return !!v; }
    num(v) {
        if (typeof v === 'number')
            return v;
        const n = Number(v);
        if (Number.isNaN(n))
            throw new RuntimeError(`Not a number: ${String(v)}`);
        return n;
    }
    equals(a, b) { return a === b; }
}
exports.CpsEvalVisitor = CpsEvalVisitor;
//# sourceMappingURL=CpsEvalVisitor.js.map