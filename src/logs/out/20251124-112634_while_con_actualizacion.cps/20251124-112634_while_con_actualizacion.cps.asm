# mips generado por compiscript
# program: 20251124-112634_while_con_actualizacion.cps

.data
__gp_base: .space 256

.text
.globl main
main:
la $gp, __gp_base
li $t0, 0
sw $t0, 0($gp)
li $t1, 3
sw $t1, 4($gp)
WHILE_START1:
lw $t2, 4($gp)
# getValueReg: src=gp[4] (mem $gp+4) -> $t2 (name=gp[4]_tmp)
lw $t3, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t3 (name=t0)
slt $t3, $t3, $t2
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t3
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t3, right=0 en $at
# emitCondBranch: emitiendo bgt $t3, $at, WHILE_BODY2
bgt $t3, $at, WHILE_BODY2
j WHILE_END3
WHILE_BODY2:
lw $t4, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t4 (name=t1)
li $at, 1
add $t4, $t4, $at
sw $t4, 0($gp)
j WHILE_START1
WHILE_END3:
# fin de main (toplevel)
li $v0, 10
syscall
