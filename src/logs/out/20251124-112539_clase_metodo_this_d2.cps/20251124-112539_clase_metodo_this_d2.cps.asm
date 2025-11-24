# mips generado por compiscript
# program: 20251124-112539_clase_metodo_this_d2.cps

.data
__gp_base: .space 256

.text
.globl main
Box_constructor:
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
Box_inc:
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
# getValueReg: acceso fp[16] fuera de frame_size=16, se permite la carga (advertencia)
lw $t3, 16($fp)
# getValueReg: src=fp[16] (mem $fp+16) -> $t3 (name=fp[16]_tmp)
# getValueReg: src=t0 (temp en reg existente) -> $t2
add $t2, $t2, $t3
# getValueReg: src=t3 (temp en reg existente) -> $t2
move $v0, $t2
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
# newobj t0 = newobj Box, size=4
li $a0, 4
li $v0, 9
syscall
# newobj: puntero -> temp t0 en $v0
# param t0
# param 10
# call Box_constructor n_args=2
# getValueReg: src=t0 (temp en reg existente) -> $v0
move $s0, $v0
# call Box_constructor: this_reg=$s0 inicializado desde t0
li $t4, 10
# getValueReg: src=10 (imm) -> $t4 (name=10)
addiu $sp, $sp, -4
sw $t4, 0($sp)
jal Box_constructor
addiu $sp, $sp, 4
# assign a slot protegido fp[0] (old fp/ra), se ignora
# param fp[0]
# param 5
# call Box_inc n_args=2
lw $t5, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t5 (name=fp[0]_tmp)
move $s0, $t5
# call Box_inc: this_reg=$s0 inicializado desde fp[0]
li $t6, 5
# getValueReg: src=5 (imm) -> $t6 (name=5)
addiu $sp, $sp, -4
sw $t6, 0($sp)
jal Box_inc
addiu $sp, $sp, 4
sw $t1, 8($fp)
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
