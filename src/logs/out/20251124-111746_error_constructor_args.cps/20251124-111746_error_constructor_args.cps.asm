# mips generado por compiscript
# program: 20251124-111746_error_constructor_args.cps

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
# getValueReg: acceso fp[20] fuera de frame_size=16, se permite la carga (advertencia)
lw $t0, 20($fp)
# getValueReg: src=fp[20] (mem $fp+20) -> $t0 (name=fp[20]_tmp)
# getValueReg: acceso fp[16] fuera de frame_size=16, se permite la carga (advertencia)
lw $t1, 16($fp)
# getValueReg: src=fp[16] (mem $fp+16) -> $t1 (name=t0)
add $t1, $t1, $t0
li $t2, 0
# getValueReg: src=t2 (temp en reg existente) -> $t2
move $t5, $t2
addu $t6, $s0, $t5
# getValueReg: src=t0 (temp en reg existente) -> $t1
sw $t1, 0($t6)
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
main:
la $gp, __gp_base
# newobj t3 = newobj A, size=4
li $a0, 4
li $v0, 9
syscall
# newobj: puntero -> temp t3 en $v0
# param t3
# param 1
# call A_constructor n_args=2
# getValueReg: src=t3 (temp en reg existente) -> $v0
move $s0, $v0
# call A_constructor: this_reg=$s0 inicializado desde t3
li $t3, 1
# getValueReg: src=1 (imm) -> $t3 (name=1)
addiu $sp, $sp, -4
sw $t3, 0($sp)
jal A_constructor
addiu $sp, $sp, 4
sw $v0, 0($gp)
# fin de main (toplevel)
li $v0, 10
syscall
