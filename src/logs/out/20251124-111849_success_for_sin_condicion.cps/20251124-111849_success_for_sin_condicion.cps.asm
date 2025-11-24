# mips generado por compiscript
# program: 20251124-111849_success_for_sin_condicion.cps

.data
__gp_base: .space 256

.text
.globl main
main:
la $gp, __gp_base
li $t0, 0
sw $t0, 0($gp)
li $t1, 0
sw $t1, 0($gp)
FOR_START1:
j FOR_BODY2
FOR_BODY2:
lw $t2, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t2 (name=t0)
li $at, 3
seq $t2, $t2, $at
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t2
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t2, right=0 en $at
# emitCondBranch: emitiendo bgt $t2, $at, IF_THEN5
bgt $t2, $at, IF_THEN5
j IF_END6
IF_THEN5:
j FOR_END3
IF_END6:
j FOR_START1
FOR_END3:
# fin de main (toplevel)
li $v0, 10
syscall
