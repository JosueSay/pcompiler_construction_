# mips generado por compiscript
# program: 20251124-111537_btest1.cps

.data
__gp_base: .space 256

.text
.globl main
m:
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
main:
# prologo frame_size=16
la $gp, __gp_base
# init $gp con base de globals (__gp_base)
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $t1, 0
sw $t1, 8($fp)
WHILE_START1:
lw $t2, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t2 (name=t0)
li $at, 20
sle $t2, $t2, $at
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t2
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t2, right=0 en $at
# emitCondBranch: emitiendo bgt $t2, $at, WHILE_BODY2
bgt $t2, $at, WHILE_BODY2
j WHILE_END3
WHILE_BODY2:
lw $t3, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t3 (name=t1)
li $at, 1
add $t3, $t3, $at
sw $t3, 8($fp)
# param fp[8]
# call m n_args=1
lw $t4, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t4 (name=fp[8]_tmp)
move $s0, $t4
# call m: this_reg=$s0 inicializado desde fp[8]
jal m
j WHILE_START1
WHILE_END3:
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
