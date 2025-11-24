# mips generado por compiscript
# program: 20251124-111751_success_atrib_acceso.cps

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
main:
la $gp, __gp_base
# newobj t2 = newobj A, size=4
li $a0, 4
li $v0, 9
syscall
# newobj: puntero -> temp t2 en $v0
# param t2
# param 5
# call A_constructor n_args=2
# getValueReg: src=t2 (temp en reg existente) -> $v0
move $s0, $v0
# call A_constructor: this_reg=$s0 inicializado desde t2
li $t1, 5
# getValueReg: src=5 (imm) -> $t1 (name=5)
addiu $sp, $sp, -4
sw $t1, 0($sp)
jal A_constructor
addiu $sp, $sp, 4
sw $v0, 0($gp)
# getValueReg: src=gp -> $gp
li $t5, 0
# index_load: idx inmediato 0 -> $t5
addu $t6, $gp, $t5
lw $t2, 0($t6)
li $t3, 0
# getValueReg: src=t3 (temp en reg existente) -> $t2
# getValueReg: src=t4 (temp en reg existente) -> $t3
move $t5, $t3
addu $t6, $t2, $t5
lw $t4, 0($t6)
sw $t0, 8($gp)
# fin de main (toplevel)
li $v0, 10
syscall
