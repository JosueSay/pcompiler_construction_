# mips generado por compiscript
# program: 20251124-112625_switch_con_fallthrough_y_break.cps

.data
__gp_base: .space 256

.text
.globl main
main:
la $gp, __gp_base
li $t0, 1
sw $t0, 0($gp)
li $t1, 0
sw $t1, 4($gp)
# emitCondBranch: raw='gp[0] == 0' -> left='gp[0]', op='==', right='0', branch_on_true=True
lw $t2, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t2 (name=gp[0]_tmp)
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=gp[0] en $t2, right=0 en $at
# emitCondBranch: emitiendo beq $t2, $at, Lcase3
beq $t2, $at, Lcase3
# emitCondBranch: raw='gp[0] == 1' -> left='gp[0]', op='==', right='1', branch_on_true=True
lw $t3, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t3 (name=gp[0]_tmp)
# emitCondBranch: right inmediato 1 -> $at (no pisa left)
li $at, 1
# emitCondBranch: regs -> left=gp[0] en $t3, right=1 en $at
# emitCondBranch: emitiendo beq $t3, $at, Lcase4
beq $t3, $at, Lcase4
j Ldef2
Lcase3:
li $t4, 10
sw $t4, 4($gp)
j Lend1
Lcase4:
li $t5, 20
sw $t5, 4($gp)
Ldef2:
lw $t6, 4($gp)
# getValueReg: src=gp[4] (mem $gp+4) -> $t6 (name=t0)
li $at, 1
add $t6, $t6, $at
sw $t6, 4($gp)
Lend1:
# fin de main (toplevel)
li $v0, 10
syscall
