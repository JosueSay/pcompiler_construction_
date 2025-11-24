# mips generado por compiscript
# program: 20251124-112635_while_update_d2.cps

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
li $t0, 0
# assign a slot protegido fp[0] (old fp/ra), se ignora
li $t1, 3
# assign a slot protegido fp[4] (old fp/ra), se ignora
li $t2, 0
sw $t2, 8($fp)
WHILE_START1:
lw $t3, 4($fp)
# getValueReg: src=fp[4] (mem $fp+4) -> $t3 (name=fp[4]_tmp)
lw $t4, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t4 (name=t0)
slt $t4, $t4, $t3
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t4
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t4, right=0 en $at
# emitCondBranch: emitiendo bgt $t4, $at, WHILE_BODY2
bgt $t4, $at, WHILE_BODY2
j WHILE_END3
WHILE_BODY2:
lw $t5, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t5 (name=fp[0]_tmp)
lw $t6, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t6 (name=t1)
add $t6, $t6, $t5
sw $t6, 8($fp)
lw $t7, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t7 (name=t1)
li $at, 1
add $t7, $t7, $at
# assign a slot protegido fp[0] (old fp/ra), se ignora
j WHILE_START1
WHILE_END3:
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
