# mips generado por compiscript
# program: 20251124-112540_clase_constructor_y_metodo.cps

.data
__gp_base: .space 256

.text
.globl main
Counter_constructor:
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
Counter_inc:
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
li $at, 1
add $t2, $t2, $at
li $t3, 0
# getValueReg: src=t1 (temp en reg existente) -> $t1
move $t5, $t1
addu $t6, $s0, $t5
# getValueReg: src=t3 (temp en reg existente) -> $t2
sw $t2, 0($t6)
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
Counter_get:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $t4, 0
# getValueReg: src=t2 (temp en reg existente) -> $t3
move $t5, $t3
addu $t6, $s0, $t5
lw $t5, 0($t6)
# getValueReg: src=t0 (temp en reg existente) -> $t5
move $v0, $t5
# return t0 -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
main:
la $gp, __gp_base
# newobj t3 = newobj Counter, size=4
li $a0, 4
li $v0, 9
syscall
# newobj: puntero -> temp t3 en $v0
# param t3
# param 5
# call Counter_constructor n_args=2
# getValueReg: src=t3 (temp en reg existente) -> $v0
move $s0, $v0
# call Counter_constructor: this_reg=$s0 inicializado desde t3
li $t6, 5
# getValueReg: src=5 (imm) -> $t6 (name=5)
addiu $sp, $sp, -4
sw $t6, 0($sp)
jal Counter_constructor
addiu $sp, $sp, 4
sw $t2, 0($gp)
# param gp[0]
# call Counter_inc n_args=1
lw $t7, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t7 (name=gp[0]_tmp)
move $s0, $t7
# call Counter_inc: this_reg=$s0 inicializado desde gp[0]
jal Counter_inc
# param gp[0]
# call Counter_get n_args=1
lw $t8, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t8 (name=gp[0]_tmp)
move $s0, $t8
# call Counter_get: this_reg=$s0 inicializado desde gp[0]
jal Counter_get
sw $t5, 8($gp)
# fin de main (toplevel)
li $v0, 10
syscall
