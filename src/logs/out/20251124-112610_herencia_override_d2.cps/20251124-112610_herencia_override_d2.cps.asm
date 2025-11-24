# mips generado por compiscript
# program: 20251124-112610_herencia_override_d2.cps

.data
__gp_base: .space 256

.text
.globl main
A_constructor:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $t0, 0
# getValueReg: src=t1 (temp en reg existente) -> $t0
move $t5, $t0
addu $t6, $s0, $t5
lw $t7, 16($fp)
sw $t7, 0($t6)
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
A_get:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $t1, 0
# getValueReg: src=t2 (temp en reg existente) -> $t0
move $t5, $t0
addu $t6, $s0, $t5
lw $t2, 0($t6)
# getValueReg: src=t0 (temp en reg existente) -> $t2
move $v0, $t2
# return t0 -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
B_get:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $t3, 0
# getValueReg: src=t2 (temp en reg existente) -> $t1
move $t5, $t1
addu $t6, $s0, $t5
lw $t4, 0($t6)
# getValueReg: src=t0 (temp en reg existente) -> $t4
li $at, 1
add $t4, $t4, $at
# getValueReg: src=t3 (temp en reg existente) -> $t4
move $v0, $t4
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
# newobj t0 = newobj A, size=4
li $a0, 4
li $v0, 9
syscall
# newobj: puntero -> temp t0 en $v0
# param t0
# param 3
# call A_constructor n_args=2
# getValueReg: src=t0 (temp en reg existente) -> $v0
move $s0, $v0
# call A_constructor: this_reg=$s0 inicializado desde t0
li $t5, 3
# getValueReg: src=3 (imm) -> $t5 (name=3)
addiu $sp, $sp, -4
sw $t5, 0($sp)
jal A_constructor
addiu $sp, $sp, 4
# assign a slot protegido fp[0] (old fp/ra), se ignora
# newobj t0 = newobj B, size=4
li $a0, 4
li $v0, 9
syscall
# newobj: puntero -> temp t0 en $v0
# param t0
# param 4
# call A_constructor n_args=2
# getValueReg: src=t0 (temp en reg existente) -> $v0
move $s0, $v0
# call A_constructor: this_reg=$s0 inicializado desde t0
li $t6, 4
# getValueReg: src=4 (imm) -> $t6 (name=4)
addiu $sp, $sp, -4
sw $t6, 0($sp)
jal A_constructor
addiu $sp, $sp, 4
sw $t2, 8($fp)
# param fp[0]
# call A_get n_args=1
lw $t7, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t7 (name=fp[0]_tmp)
move $s0, $t7
# call A_get: this_reg=$s0 inicializado desde fp[0]
jal A_get
sw $t3, 16($fp)
# param fp[8]
# call B_get n_args=1
lw $t8, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t8 (name=fp[8]_tmp)
move $s0, $t8
# call B_get: this_reg=$s0 inicializado desde fp[8]
jal B_get
sw $t3, 20($fp)
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
