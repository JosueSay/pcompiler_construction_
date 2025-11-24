# mips generado por compiscript
# program: 20251124-112617_negacion.cps

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
li $t0, 1
# assign a slot protegido fp[0] (old fp/ra), se ignora
lw $t1, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t1 (name=t0)
li $at, 1
seq $t1, $t1, $at
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t1
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t1, right=0 en $at
# emitCondBranch: emitiendo bgt $t1, $at, IF_ELSE3
bgt $t1, $at, IF_ELSE3
j IF_THEN1
IF_THEN1:
li $t2, 9
# assign a slot protegido fp[0] (old fp/ra), se ignora
j IF_END2
IF_ELSE3:
li $t3, 7
# assign a slot protegido fp[0] (old fp/ra), se ignora
IF_END2:
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
