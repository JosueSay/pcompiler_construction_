# mips generado por compiscript
# program: 20251124-111543_btest6.cps

.data
__gp_base: .space 256

.text
.globl main
factorial:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
lw $t0, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t0 (name=t0)
li $at, 0
seq $t0, $t0, $at
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t0
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t0, right=0 en $at
# emitCondBranch: emitiendo bgt $t0, $at, IF_THEN1
bgt $t0, $at, IF_THEN1
j IF_ELSE3
IF_THEN1:
li $t1, 1
# getValueReg: src=1 (imm) -> $t1 (name=1)
move $v0, $t1
# return 1 -> $v0
IF_ELSE3:
lw $t2, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t2 (name=t1)
li $at, 1
sub $t2, $t2, $at
# param t1
# call factorial n_args=1
# getValueReg: src=t1 (temp en reg existente) -> $t2
move $s0, $t2
# call factorial: this_reg=$s0 inicializado desde t1
jal factorial
# getValueReg: src=t2 (temp en reg existente) -> $v0
lw $t3, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t3 (name=t1)
mul $t3, $t3, $v0
# getValueReg: src=t1 (temp en reg existente) -> $t3
move $v0, $t3
# return t1 -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
main:
# prologo frame_size=16
la $gp, __gp_base
# init $gp con base de globals (__gp_base)
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $t4, 0
# assign a slot protegido fp[4] (old fp/ra), se ignora
WHILE_START4:
lw $t5, 4($fp)
# getValueReg: src=fp[4] (mem $fp+4) -> $t5 (name=t0)
li $at, 10
slt $t5, $t5, $at
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t5
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t5, right=0 en $at
# emitCondBranch: emitiendo bgt $t5, $at, WHILE_BODY5
bgt $t5, $at, WHILE_BODY5
j WHILE_END6
WHILE_BODY5:
lw $t6, 4($fp)
# getValueReg: src=fp[4] (mem $fp+4) -> $t6 (name=t0)
li $at, 5
sne $t6, $t6, $at
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t6
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t6, right=0 en $at
# emitCondBranch: emitiendo bgt $t6, $at, IF_THEN7
bgt $t6, $at, IF_THEN7
j IF_END8
IF_THEN7:
# param fp[4]
# call factorial n_args=1
lw $t7, 4($fp)
# getValueReg: src=fp[4] (mem $fp+4) -> $t7 (name=fp[4]_tmp)
move $s0, $t7
# call factorial: this_reg=$s0 inicializado desde fp[4]
jal factorial
# assign a slot protegido fp[0] (old fp/ra), se ignora
IF_END8:
lw $t8, 4($fp)
# getValueReg: src=fp[4] (mem $fp+4) -> $t8 (name=t2)
li $at, 1
add $t8, $t8, $at
# assign a slot protegido fp[4] (old fp/ra), se ignora
j WHILE_START4
WHILE_END6:
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
