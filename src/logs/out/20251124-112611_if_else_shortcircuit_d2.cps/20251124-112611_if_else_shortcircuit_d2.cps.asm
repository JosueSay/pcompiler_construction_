# mips generado por compiscript
# program: 20251124-112611_if_else_shortcircuit_d2.cps

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
li $t0, 15
# assign a slot protegido fp[0] (old fp/ra), se ignora
li $t1, 5
# assign a slot protegido fp[4] (old fp/ra), se ignora
lw $t2, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t2 (name=t0)
li $at, 10
slt $t2, $t2, $at
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t2
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t2, right=0 en $at
# emitCondBranch: emitiendo bgt $t2, $at, IF_THEN1
bgt $t2, $at, IF_THEN1
j Lor4
Lor4:
lw $t3, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t3 (name=t0)
li $at, 20
sgt $t3, $t3, $at
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t3
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t3, right=0 en $at
# emitCondBranch: emitiendo bgt $t3, $at, Land5
bgt $t3, $at, Land5
j IF_ELSE3
Land5:
lw $t4, 4($fp)
# getValueReg: src=fp[4] (mem $fp+4) -> $t4 (name=fp[4]_tmp)
lw $t5, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t5 (name=t0)
sne $t5, $t5, $t4
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t5
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t5, right=0 en $at
# emitCondBranch: emitiendo bgt $t5, $at, IF_THEN1
bgt $t5, $at, IF_THEN1
j IF_ELSE3
IF_THEN1:
li $t6, 0
# assign a slot protegido fp[4] (old fp/ra), se ignora
j IF_END2
IF_ELSE3:
li $t7, 1
# assign a slot protegido fp[4] (old fp/ra), se ignora
IF_END2:
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
