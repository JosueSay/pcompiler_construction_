# mips generado por compiscript
# program: 20251124-111845_error_switch_case_incompatible.cps

.data
__gp_base: .space 256
__str_0: .asciiz "uno"

.text
.globl main
main:
la $gp, __gp_base
li $t0, 1
sw $t0, 0($gp)
# emitCondBranch: raw='gp[0] == "uno"' -> left='gp[0]', op='==', right='"uno"', branch_on_true=True
lw $t1, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t1 (name=gp[0]_tmp)
la $t2, __str_0
# getValueReg: src="uno" (string) -> $t2 (label=__str_0, name=__str_0)
# emitCondBranch: regs -> left=gp[0] en $t1, right="uno" en $t2
# emitCondBranch: emitiendo beq $t1, $t2, Lcase3
beq $t1, $t2, Lcase3
j Ldef2
Lcase3:
Ldef2:
Lend1:
# fin de main (toplevel)
li $v0, 10
syscall
