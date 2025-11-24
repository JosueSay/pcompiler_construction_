# mips generado por compiscript
# program: 20251124-111545_btest7.cps

.data
__gp_base: .space 256

.text
.globl main
gcd:
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
lw $t1, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $t1 (name=fp[12]_tmp)
move $v0, $t1
# return fp[12] -> $v0
IF_ELSE3:
lw $t2, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t2 (name=fp[8]_tmp)
lw $t3, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $t3 (name=t1)
div $t3, $t3, $t2
lw $t4, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t4 (name=fp[8]_tmp)
# getValueReg: src=t1 (temp en reg existente) -> $t3
mul $t3, $t3, $t4
# getValueReg: src=t2 (temp en reg existente) -> $t3
lw $t5, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $t5 (name=t2)
sub $t5, $t5, $t3
# param fp[8]
# param t2
# call gcd n_args=2
lw $t6, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t6 (name=fp[8]_tmp)
move $s0, $t6
# call gcd: this_reg=$s0 inicializado desde fp[8]
# getValueReg: src=t2 (temp en reg existente) -> $t5
addiu $sp, $sp, -4
sw $t5, 0($sp)
jal gcd
addiu $sp, $sp, 4
# getValueReg: src=t3 (temp en reg existente) -> $v0
# return t3 -> $v0
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
li $t7, 10
# assign a slot protegido fp[0] (old fp/ra), se ignora
li $t8, 5
# assign a slot protegido fp[4] (old fp/ra), se ignora
# param fp[0]
# param fp[4]
# call gcd n_args=2
lw $t9, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t9 (name=fp[0]_tmp)
move $s0, $t9
# call gcd: this_reg=$s0 inicializado desde fp[0]
lw $s1, 4($fp)
# getValueReg: src=fp[4] (mem $fp+4) -> $s1 (name=fp[4]_tmp)
addiu $sp, $sp, -4
sw $s1, 0($sp)
jal gcd
addiu $sp, $sp, 4
sw $t0, 8($fp)
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
