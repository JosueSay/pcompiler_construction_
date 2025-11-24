# mips generado por compiscript
# program: 20251124-111540_btest3.cps

.data
__gp_base: .space 256

.text
.globl main
OutputInt:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
InputInt:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $t0, 0
# getValueReg: src=0 (imm) -> $t0 (name=0)
move $v0, $t0
# return 0 -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
fibonacci:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
lw $t1, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t1 (name=t0)
li $at, 0
seq $t1, $t1, $at
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t1
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t1, right=0 en $at
# emitCondBranch: emitiendo bgt $t1, $at, IF_THEN1
bgt $t1, $at, IF_THEN1
j IF_ELSE3
IF_THEN1:
li $t2, 1
# assign a slot protegido fp[0] (old fp/ra), se ignora
j IF_END2
IF_ELSE3:
lw $t3, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t3 (name=t0)
li $at, 1
seq $t3, $t3, $at
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t3
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t3, right=0 en $at
# emitCondBranch: emitiendo bgt $t3, $at, IF_THEN4
bgt $t3, $at, IF_THEN4
j IF_ELSE6
IF_THEN4:
li $t4, 1
# assign a slot protegido fp[0] (old fp/ra), se ignora
j IF_END5
IF_ELSE6:
lw $t5, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t5 (name=t1)
li $at, 1
sub $t5, $t5, $at
# param t1
# call fibonacci n_args=1
# getValueReg: src=t1 (temp en reg existente) -> $t5
move $s0, $t5
# call fibonacci: this_reg=$s0 inicializado desde t1
jal fibonacci
lw $t6, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t6 (name=t1)
li $at, 2
sub $t6, $t6, $at
# param t1
# call fibonacci n_args=1
# getValueReg: src=t1 (temp en reg existente) -> $t6
move $s0, $t6
# call fibonacci: this_reg=$s0 inicializado desde t1
jal fibonacci
# getValueReg: src=t3 (temp en reg existente) -> $v0
# ERROR: temp t2 usado sin valor inicial
# binary t1 := t2 + t3 (no soportado)
# assign a slot protegido fp[0] (old fp/ra), se ignora
IF_END5:
IF_END2:
lw $t7, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t7 (name=fp[0]_tmp)
move $v0, $t7
# return fp[0] -> $v0
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
li $t8, 0
sw $t8, 8($fp)
WHILE_START7:
lw $t9, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t9 (name=t0)
li $at, 20
sle $t9, $t9, $at
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t9
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t9, right=0 en $at
# emitCondBranch: emitiendo bgt $t9, $at, WHILE_BODY8
bgt $t9, $at, WHILE_BODY8
j WHILE_END9
WHILE_BODY8:
# param fp[8]
# call fibonacci n_args=1
lw $s1, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $s1 (name=fp[8]_tmp)
move $s0, $s1
# call fibonacci: this_reg=$s0 inicializado desde fp[8]
jal fibonacci
# assign a slot protegido fp[4] (old fp/ra), se ignora
# param fp[4]
# call OutputInt n_args=1
lw $s2, 4($fp)
# getValueReg: src=fp[4] (mem $fp+4) -> $s2 (name=fp[4]_tmp)
move $s0, $s2
# call OutputInt: this_reg=$s0 inicializado desde fp[4]
jal OutputInt
lw $s3, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $s3 (name=t2)
li $at, 1
add $s3, $s3, $at
sw $s3, 8($fp)
j WHILE_START7
WHILE_END9:
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
