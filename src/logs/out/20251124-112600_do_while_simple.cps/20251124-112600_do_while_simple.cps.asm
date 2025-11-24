# mips generado por compiscript
# program: 20251124-112600_do_while_simple.cps

.data
__gp_base: .space 256

.text
.globl main
main:
la $gp, __gp_base
li $t0, 0
sw $t0, 0($gp)
DO_BODY1:
lw $t1, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t1 (name=t0)
li $at, 2
add $t1, $t1, $at
sw $t1, 0($gp)
DO_COND2:
lw $t2, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t2 (name=t1)
li $at, 5
slt $t2, $t2, $at
# emitCondBranch: raw='t1 > 0' -> left='t1', op='>', right='0', branch_on_true=True
# getValueReg: src=t1 (temp en reg existente) -> $t2
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t1 en $t2, right=0 en $at
# emitCondBranch: emitiendo bgt $t2, $at, DO_BODY1
bgt $t2, $at, DO_BODY1
j DO_END3
DO_END3:
# fin de main (toplevel)
li $v0, 10
syscall
