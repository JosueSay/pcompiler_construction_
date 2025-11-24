# mips generado por compiscript
# program: 20251124-111852_success_while_boolean.cps

.data
__gp_base: .space 256

.text
.globl main
main:
la $gp, __gp_base
li $t0, 0
sw $t0, 0($gp)
WHILE_START1:
lw $t1, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t1 (name=t0)
li $at, 3
slt $t1, $t1, $at
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t1
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t1, right=0 en $at
# emitCondBranch: emitiendo bgt $t1, $at, WHILE_BODY2
bgt $t1, $at, WHILE_BODY2
j WHILE_END3
WHILE_BODY2:
lw $t2, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t2 (name=t1)
li $at, 1
add $t2, $t2, $at
sw $t2, 0($gp)
j WHILE_START1
WHILE_END3:
# fin de main (toplevel)
li $v0, 10
syscall
