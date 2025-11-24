# mips generado por compiscript
# program: 20251124-111851_success_switch_tipos_compatibles.cps

.data
__gp_base: .space 256

.text
.globl main
main:
la $gp, __gp_base
li $t0, 2
sw $t0, 0($gp)
# emitCondBranch: raw='gp[0] == 1' -> left='gp[0]', op='==', right='1', branch_on_true=True
lw $t1, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t1 (name=gp[0]_tmp)
# emitCondBranch: right inmediato 1 -> $at (no pisa left)
li $at, 1
# emitCondBranch: regs -> left=gp[0] en $t1, right=1 en $at
# emitCondBranch: emitiendo beq $t1, $at, Lcase3
beq $t1, $at, Lcase3
# emitCondBranch: raw='gp[0] == 2' -> left='gp[0]', op='==', right='2', branch_on_true=True
lw $t2, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t2 (name=gp[0]_tmp)
# emitCondBranch: right inmediato 2 -> $at (no pisa left)
li $at, 2
# emitCondBranch: regs -> left=gp[0] en $t2, right=2 en $at
# emitCondBranch: emitiendo beq $t2, $at, Lcase4
beq $t2, $at, Lcase4
j Ldef2
Lcase3:
Lcase4:
Ldef2:
Lend1:
# fin de main (toplevel)
li $v0, 10
syscall
