# mips generado por compiscript
# program: 20251124-111754_success_herencia_override.cps

.data
__gp_base: .space 256
__str_0: .asciiz "Toby"

.text
.globl main
Animal_constructor:
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
Animal_hablar:
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
# binary t3 := t0 + " hace ruido." con strings (concat simplificada: dst copia de t0)
# getValueReg: src=t3 (temp en reg existente) -> $t2
move $v0, $t2
# return t3 -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
Perro_hablar:
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
# binary t3 := t0 + " ladra." con strings (concat simplificada: dst copia de t0)
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
la $gp, __gp_base
# newobj t0 = newobj Perro, size=8
li $a0, 8
li $v0, 9
syscall
# newobj: puntero -> temp t0 en $v0
# param t0
# param "Toby"
# call Animal_constructor n_args=2
# getValueReg: src=t0 (temp en reg existente) -> $v0
move $s0, $v0
# call Animal_constructor: this_reg=$s0 inicializado desde t0
la $t5, __str_0
# getValueReg: src="Toby" (string) -> $t5 (label=__str_0, name=__str_0)
addiu $sp, $sp, -4
sw $t5, 0($sp)
jal Animal_constructor
addiu $sp, $sp, 4
sw $v0, 0($gp)
# param gp[0]
# call Perro_hablar n_args=1
lw $t6, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t6 (name=gp[0]_tmp)
move $s0, $t6
# call Perro_hablar: this_reg=$s0 inicializado desde gp[0]
jal Perro_hablar
sw $v0, 8($gp)
# fin de main (toplevel)
li $v0, 10
syscall
