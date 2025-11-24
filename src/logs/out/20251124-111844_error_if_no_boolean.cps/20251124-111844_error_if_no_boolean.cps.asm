# mips generado por compiscript
# program: 20251124-111844_error_if_no_boolean.cps

.data
__gp_base: .space 256

.text
.globl main
main:
la $gp, __gp_base
li $t0, 1
sw $t0, 0($gp)
# emitCondBranch: raw='gp[0] > 0' -> left='gp[0]', op='>', right='0', branch_on_true=True
lw $t1, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t1 (name=gp[0]_tmp)
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=gp[0] en $t1, right=0 en $at
# emitCondBranch: emitiendo bgt $t1, $at, IF_THEN1
bgt $t1, $at, IF_THEN1
j IF_END2
IF_THEN1:
IF_END2:
# fin de main (toplevel)
li $v0, 10
syscall
