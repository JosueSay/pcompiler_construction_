# mips generado por compiscript
# program: 20251124-112603_field_access_store_d1.cps

.data
__gp_base: .space 256

.text
.globl main
C_constructor:
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
main:
# prologo frame_size=16
la $gp, __gp_base
# init $gp con base de globals (__gp_base)
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
# newobj t0 = newobj C, size=4
li $a0, 4
li $v0, 9
syscall
# newobj: puntero -> temp t0 en $v0
# param t0
# param 10
# call C_constructor n_args=2
# getValueReg: src=t0 (temp en reg existente) -> $v0
move $s0, $v0
# call C_constructor: this_reg=$s0 inicializado desde t0
li $t1, 10
# getValueReg: src=10 (imm) -> $t1 (name=10)
addiu $sp, $sp, -4
sw $t1, 0($sp)
jal C_constructor
addiu $sp, $sp, 4
# assign a slot protegido fp[0] (old fp/ra), se ignora
# getValueReg: src=fp no soportado explícitamente -> devuelve None
# index_load t2 := fp[0] (base no soportada)
li $t2, 0
# ERROR: temp t2 usado sin valor inicial
# index_load t1 := t2[t4] (base no soportada)
sw $t0, 8($fp)
lw $t3, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t3 (name=t5)
li $at, 2
add $t3, $t3, $at
li $t4, 0
# getValueReg: src=fp no soportado explícitamente -> devuelve None
# index_store fp[t4] := t5 (base no soportada)
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
