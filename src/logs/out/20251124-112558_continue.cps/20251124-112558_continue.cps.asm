# mips generado por compiscript
# program: 20251124-112558_continue.cps

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
li $t1, 0
# assign a slot protegido fp[4] (old fp/ra), se ignora
WHILE_START1:
lw $t2, 4($fp)
# getValueReg: src=fp[4] (mem $fp+4) -> $t2 (name=t0)
li $at, 5
slt $t2, $t2, $at
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t2
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t2, right=0 en $at
# emitCondBranch: emitiendo bgt $t2, $at, WHILE_BODY2
bgt $t2, $at, WHILE_BODY2
j WHILE_END3
WHILE_BODY2:
lw $t3, 4($fp)
# getValueReg: src=fp[4] (mem $fp+4) -> $t3 (name=t1)
li $at, 1
add $t3, $t3, $at
# assign a slot protegido fp[4] (old fp/ra), se ignora
lw $t4, 4($fp)
# getValueReg: src=fp[4] (mem $fp+4) -> $t4 (name=t1)
li $at, 2
rem $t4, $t4, $at
# getValueReg: src=t1 (temp en reg existente) -> $t4
li $at, 0
seq $t4, $t4, $at
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t4
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t4, right=0 en $at
# emitCondBranch: emitiendo bgt $t4, $at, IF_THEN4
bgt $t4, $at, IF_THEN4
j IF_END5
IF_THEN4:
j WHILE_START1
IF_END5:
lw $t5, 4($fp)
# getValueReg: src=fp[4] (mem $fp+4) -> $t5 (name=fp[4]_tmp)
lw $t6, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t6 (name=t1)
add $t6, $t6, $t5
# assign a slot protegido fp[0] (old fp/ra), se ignora
j WHILE_START1
WHILE_END3:
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
