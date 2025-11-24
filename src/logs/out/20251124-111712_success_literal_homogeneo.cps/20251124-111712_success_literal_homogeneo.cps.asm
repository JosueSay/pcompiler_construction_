# mips generado por compiscript
# program: 20251124-111712_success_literal_homogeneo.cps

.data
__gp_base: .space 256

.text
.globl main
main:
la $gp, __gp_base
# assign gp[0] := [1,2,3] (no soportado aún)
# quad no manejado: len
# emitCondBranch: raw='0<0' -> left='0', op='<', right='0', branch_on_true=True
li $t0, 0
# getValueReg: src=0 (imm) -> $t0 (name=0)
li $t1, 0
# getValueReg: src=0 (imm) -> $t1 (name=0)
# emitCondBranch: regs -> left=0 en $t0, right=0 en $t1
# emitCondBranch: emitiendo blt $t0, $t1, oob1
blt $t0, $t1, oob1
# emitCondBranch: raw='0>=t1' -> left='0', op='>=', right='t1', branch_on_true=True
li $t2, 0
# getValueReg: src=0 (imm) -> $t2 (name=0)
# ERROR: temp t1 usado sin valor inicial
# emitCondBranch: regs -> left=0 en $t2, right=t1 en None
# branch sobre '0>=t1' no soportado (operandos)
j ok2
oob1:
# call __bounds_error n_args=0
jal __bounds_error
ok2:
lw $t6, 0($gp)
li $t5, 0
# index_load: idx inmediato 0 -> $t5
addu $t6, $t6, $t5
lw $t3, 0($t6)
sw $t3, 8($gp)
# assign gp[12] := [[1,2],[3,4]] (no soportado aún)
# quad no manejado: len
# emitCondBranch: raw='1<0' -> left='1', op='<', right='0', branch_on_true=True
li $t4, 1
# getValueReg: src=1 (imm) -> $t4 (name=1)
li $t5, 0
# getValueReg: src=0 (imm) -> $t5 (name=0)
# emitCondBranch: regs -> left=1 en $t4, right=0 en $t5
# emitCondBranch: emitiendo blt $t4, $t5, oob3
blt $t4, $t5, oob3
# emitCondBranch: raw='1>=t0' -> left='1', op='>=', right='t0', branch_on_true=True
li $t6, 1
# getValueReg: src=1 (imm) -> $t6 (name=1)
# getValueReg: src=t0 (temp en reg existente) -> $t3
# emitCondBranch: regs -> left=1 en $t6, right=t0 en $t3
# emitCondBranch: emitiendo bge $t6, $t3, oob3
bge $t6, $t3, oob3
j ok4
oob3:
# call __bounds_error n_args=0
jal __bounds_error
ok4:
lw $t6, 12($gp)
li $t5, 1
# index_load: idx inmediato 1 -> $t5
addu $t6, $t6, $t5
lw $t7, 0($t6)
sw $t7, 20($gp)
# fin de main (toplevel)
li $v0, 10
syscall
