# mips generado por compiscript
# program: 20251124-112626_switch_fallthrough_d2.cps

.data
__gp_base: .space 256

.text
.globl main
main:
# prologo frame_size=16
la $gp, __gp_base
# init $gp con base de globals (__gp_base)
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $t0, 2
# assign a slot protegido fp[0] (old fp/ra), se ignora
# quad no manejado: unary
# valor de t0 no inicializado en registros
# assign a slot protegido fp[4] (old fp/ra), se ignora
# emitCondBranch: raw='fp[0] == 1' -> left='fp[0]', op='==', right='1', branch_on_true=True
lw $t2, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t2 (name=fp[0]_tmp)
# emitCondBranch: right inmediato 1 -> $at (no pisa left)
li $at, 1
# emitCondBranch: regs -> left=fp[0] en $t2, right=1 en $at
# emitCondBranch: emitiendo beq $t2, $at, Lcase3
beq $t2, $at, Lcase3
# emitCondBranch: raw='fp[0] == 2' -> left='fp[0]', op='==', right='2', branch_on_true=True
lw $t3, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t3 (name=fp[0]_tmp)
# emitCondBranch: right inmediato 2 -> $at (no pisa left)
li $at, 2
# emitCondBranch: regs -> left=fp[0] en $t3, right=2 en $at
# emitCondBranch: emitiendo beq $t3, $at, Lcase4
beq $t3, $at, Lcase4
j Ldef2
Lcase3:
li $t4, 1
# assign a slot protegido fp[4] (old fp/ra), se ignora
Lcase4:
li $t5, 2
# assign a slot protegido fp[4] (old fp/ra), se ignora
j Lend1
Ldef2:
li $t6, 0
# assign a slot protegido fp[4] (old fp/ra), se ignora
Lend1:
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
