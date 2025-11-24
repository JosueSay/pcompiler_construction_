# mips generado por compiscript
# program: 20251124-111711_success_index_entero.cps

.data
__gp_base: .space 256

.text
.globl main
main:
la $gp, __gp_base
# assign gp[0] := [10,20,30] (no soportado aún)
li $t0, 1
sw $t0, 8($gp)
# quad no manejado: len
# emitCondBranch: raw='gp[8]<0' -> left='gp[8]', op='<', right='0', branch_on_true=True
lw $t1, 8($gp)
# getValueReg: src=gp[8] (mem $gp+8) -> $t1 (name=gp[8]_tmp)
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=gp[8] en $t1, right=0 en $at
# emitCondBranch: emitiendo blt $t1, $at, oob1
blt $t1, $at, oob1
# emitCondBranch: raw='gp[8]>=t1' -> left='gp[8]', op='>=', right='t1', branch_on_true=True
lw $t2, 8($gp)
# getValueReg: src=gp[8] (mem $gp+8) -> $t2 (name=gp[8]_tmp)
# ERROR: temp t1 usado sin valor inicial
# emitCondBranch: regs -> left=gp[8] en $t2, right=t1 en None
# branch sobre 'gp[8]>=t1' no soportado (operandos)
j ok2
oob1:
# call __bounds_error n_args=0
jal __bounds_error
ok2:
lw $t6, 0($gp)
lw $t3, 8($gp)
# getValueReg: src=gp[8] (mem $gp+8) -> $t3 (name=gp[8]_tmp)
move $t5, $t3
addu $t6, $t6, $t5
lw $t4, 0($t6)
sw $t4, 12($gp)
li $t5, 2
# quad no manejado: len
# emitCondBranch: raw='t2<0' -> left='t2', op='<', right='0', branch_on_true=True
# getValueReg: src=t2 (temp en reg existente) -> $t5
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t2 en $t5, right=0 en $at
# emitCondBranch: emitiendo blt $t5, $at, oob3
blt $t5, $at, oob3
# emitCondBranch: raw='t2>=t1' -> left='t2', op='>=', right='t1', branch_on_true=True
# getValueReg: src=t2 (temp en reg existente) -> $t5
# ERROR: temp t1 usado sin valor inicial
# emitCondBranch: regs -> left=t2 en $t5, right=t1 en None
# branch sobre 't2>=t1' no soportado (operandos)
j ok4
oob3:
# call __bounds_error n_args=0
jal __bounds_error
ok4:
lw $t6, 0($gp)
# getValueReg: src=t2 (temp en reg existente) -> $t5
addu $t6, $t6, $t5
lw $t6, 0($t6)
sw $t4, 16($gp)
# fin de main (toplevel)
li $v0, 10
syscall
