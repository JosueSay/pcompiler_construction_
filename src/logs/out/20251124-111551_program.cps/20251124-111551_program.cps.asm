# mips generado por compiscript
# program: 20251124-111551_program.cps

.data
__gp_base: .space 256
__str_0: .asciiz ""
__str_1: .asciiz "rojo"
__str_2: .asciiz "Erick"

.text
.globl main
toString:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
la $t0, __str_0
# getValueReg: src="" (string) -> $t0 (label=__str_0, name=__str_0)
move $v0, $t0
# return "" -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
Persona_constructor:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $t1, 0
# getValueReg: src=t1 (temp en reg existente) -> $t1
move $t5, $t1
addu $t6, $s0, $t5
lw $t7, 16($fp)
sw $t7, 0($t6)
li $t2, 8
# getValueReg: src=t0 (temp en reg existente) -> $t1
move $t5, $t1
addu $t6, $s0, $t5
lw $t7, 24($fp)
sw $t7, 0($t6)
li $t3, 12
# getValueReg: src=t1 (temp en reg existente) -> $t2
move $t5, $t2
addu $t6, $s0, $t5
la $t4, __str_1
# getValueReg: src="rojo" (string) -> $t4 (label=__str_1, name=__str_1)
sw $t4, 0($t6)
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
Persona_saludar:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $t5, 0
# getValueReg: src=t2 (temp en reg existente) -> $t1
move $t5, $t1
addu $t6, $s0, $t5
lw $t6, 0($t6)
# getValueReg: src=t0 (temp en reg existente) -> $t6
# binary t3 := "Hola, mi nombre es " + t0 con strings (concat simplificada: dst copia de t0)
# getValueReg: src=t3 (temp en reg existente) -> $t6
move $v0, $t6
# return t3 -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
Persona_incrementarEdad:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $t7, 8
# getValueReg: src=t2 (temp en reg existente) -> $t2
move $t5, $t2
addu $t6, $s0, $t5
lw $t8, 0($t6)
# getValueReg: acceso fp[16] fuera de frame_size=16, se permite la carga (advertencia)
lw $t9, 16($fp)
# getValueReg: src=fp[16] (mem $fp+16) -> $t9 (name=fp[16]_tmp)
# getValueReg: src=t0 (temp en reg existente) -> $t8
add $t8, $t8, $t9
li $s1, 8
# getValueReg: src=t1 (temp en reg existente) -> $t7
move $t5, $t7
addu $t6, $s0, $t5
# getValueReg: src=t3 (temp en reg existente) -> $t8
sw $t8, 0($t6)
li $s2, 8
# getValueReg: src=t2 (temp en reg existente) -> $s1
move $t5, $s1
addu $t6, $s0, $t5
lw $s3, 0($t6)
# param t0
# call toString n_args=1
# getValueReg: src=t0 (temp en reg existente) -> $s3
move $s0, $s3
# call toString: this_reg=$s0 inicializado desde t0
jal toString
# getValueReg: src=t4 (temp en reg existente) -> $v0
# binary t3 := "Ahora tengo " + t4 con strings (concat simplificada: dst copia de t4)
# getValueReg: src=t3 (temp en reg existente) -> $v0
# binary t5 := t3 + " años." con strings (concat simplificada: dst copia de t3)
# getValueReg: src=t5 (temp en reg existente) -> $v0
# return t5 -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
Estudiante_constructor:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $s4, 0
# getValueReg: src=t1 (temp en reg existente) -> $s2
move $t5, $s2
addu $t6, $s0, $t5
lw $t7, 16($fp)
sw $t7, 0($t6)
li $s5, 8
# getValueReg: src=t0 (temp en reg existente) -> $s4
move $t5, $s4
addu $t6, $s0, $t5
lw $t7, 24($fp)
sw $t7, 0($t6)
li $s6, 12
# getValueReg: src=t1 (temp en reg existente) -> $s5
move $t5, $s5
addu $t6, $s0, $t5
la $s7, __str_1
# getValueReg: src="rojo" (string) -> $s7 (label=__str_1, name=__str_1)
sw $s7, 0($t6)
li $v1, 20
# getValueReg: src=t0 (temp en reg existente) -> $s6
move $t5, $s6
addu $t6, $s0, $t5
lw $t7, 28($fp)
sw $t7, 0($t6)
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
Estudiante_estudiar:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $t0, 0
# getValueReg: src=t2 (temp en reg existente) -> $s1
move $t5, $s1
addu $t6, $s0, $t5
lw $t4, 0($t6)
# getValueReg: src=t0 (temp en reg existente) -> $s6
# binary t3 := t0 + " está estudiando en " con strings (concat simplificada: dst copia de t0)
li $t9, 20
# getValueReg: src=t4 (temp en reg existente) -> $t5
addu $t6, $s0, $t5
lw $s7, 0($t6)
# param t2
# call toString n_args=1
# getValueReg: src=t2 (temp en reg existente) -> $s7
move $s0, $s7
# call toString: this_reg=$s0 inicializado desde t2
jal toString
# getValueReg: src=t3 (temp en reg existente) -> $s6
# binary t6 := t3 + t5 con strings (concat simplificada: dst copia de t3)
# getValueReg: src=t6 (temp en reg existente) -> $s6
# binary t7 := t6 + " grado." con strings (concat simplificada: dst copia de t6)
# getValueReg: src=t7 (temp en reg existente) -> $s6
move $v0, $s6
# return t7 -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
Estudiante_promedioNotas:
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
lw $t0, 16($fp)
# getValueReg: src=fp[16] (mem $fp+16) -> $t0 (name=t0)
lw $at, 20($fp)
add $t0, $t0, $at
# getValueReg: acceso fp[24] fuera de frame_size=16, se permite la carga (advertencia)
lw $t0, 24($fp)
# getValueReg: src=fp[24] (mem $fp+24) -> $t0 (name=fp[24]_tmp)
# getValueReg: src=t0 (temp en reg existente) -> $s4
add $s4, $s4, $t0
# getValueReg: src=t1 (temp en reg existente) -> $v1
li $at, 3
div $v1, $v1, $at
# assign a slot protegido fp[0] (old fp/ra), se ignora
lw $t0, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t0 (name=fp[0]_tmp)
move $v0, $t0
# return fp[0] -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
main:
la $gp, __gp_base
la $t0, __str_0
# assign literal string "" -> $t0 (label=__str_0)
sw $t0, 0($gp)
la $t0, __str_2
# assign literal string "Erick" -> $t0 (label=__str_2)
sw $t0, 8($gp)
# newobj t3 = newobj Estudiante, size=24
li $a0, 24
li $v0, 9
syscall
# newobj: puntero -> temp t3 en $v0
# param t3
# param gp[8]
# param 20
# param 3
# call Estudiante_constructor n_args=4
# getValueReg: src=t3 (temp en reg existente) -> $v0
move $s0, $v0
# call Estudiante_constructor: this_reg=$s0 inicializado desde t3
lw $t0, 8($gp)
# getValueReg: src=gp[8] (mem $gp+8) -> $t0 (name=gp[8]_tmp)
addiu $sp, $sp, -4
sw $t0, 0($sp)
li $t0, 20
# getValueReg: src=20 (imm) -> $t0 (name=20)
addiu $sp, $sp, -4
sw $t0, 0($sp)
li $t0, 3
# getValueReg: src=3 (imm) -> $t0 (name=3)
addiu $sp, $sp, -4
sw $t0, 0($sp)
jal Estudiante_constructor
addiu $sp, $sp, 12
sw $t6, 16($gp)
# param gp[16]
# call Persona_saludar n_args=1
lw $t0, 16($gp)
# getValueReg: src=gp[16] (mem $gp+16) -> $t0 (name=gp[16]_tmp)
move $s0, $t0
# call Persona_saludar: this_reg=$s0 inicializado desde gp[16]
jal Persona_saludar
# getValueReg: src=t3 (temp en reg existente) -> $v0
# binary t0 := gp[0] + t3 con strings (concat simplificada: dst copia de t3)
# getValueReg: src=t0 (temp en reg existente) -> $v0
# binary t2 := t0 + "\n" con strings (concat simplificada: dst copia de t0)
sw $t1, 0($gp)
# param gp[16]
# call Estudiante_estudiar n_args=1
lw $t0, 16($gp)
# getValueReg: src=gp[16] (mem $gp+16) -> $t0 (name=gp[16]_tmp)
move $s0, $t0
# call Estudiante_estudiar: this_reg=$s0 inicializado desde gp[16]
jal Estudiante_estudiar
# getValueReg: src=t3 (temp en reg existente) -> $v0
# binary t0 := gp[0] + t3 con strings (concat simplificada: dst copia de t3)
# getValueReg: src=t0 (temp en reg existente) -> $v0
# binary t2 := t0 + "\n" con strings (concat simplificada: dst copia de t0)
sw $t1, 0($gp)
# param gp[16]
# param 5
# call Persona_incrementarEdad n_args=2
lw $t0, 16($gp)
# getValueReg: src=gp[16] (mem $gp+16) -> $t0 (name=gp[16]_tmp)
move $s0, $t0
# call Persona_incrementarEdad: this_reg=$s0 inicializado desde gp[16]
li $t0, 5
# getValueReg: src=5 (imm) -> $t0 (name=5)
addiu $sp, $sp, -4
sw $t0, 0($sp)
jal Persona_incrementarEdad
addiu $sp, $sp, 4
# getValueReg: src=t3 (temp en reg existente) -> $v0
# binary t0 := gp[0] + t3 con strings (concat simplificada: dst copia de t3)
# getValueReg: src=t0 (temp en reg existente) -> $v0
# binary t2 := t0 + "\n" con strings (concat simplificada: dst copia de t0)
sw $t1, 0($gp)
li $t0, 1
sw $t0, 24($gp)
WHILE_START1:
lw $t0, 24($gp)
# getValueReg: src=gp[24] (mem $gp+24) -> $t0 (name=t4)
li $at, 5
sle $t0, $t0, $at
# emitCondBranch: raw='t4 > 0' -> left='t4', op='>', right='0', branch_on_true=True
# getValueReg: src=t4 (temp en reg existente) -> $t5
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t4 en $t5, right=0 en $at
# emitCondBranch: emitiendo bgt $t5, $at, WHILE_BODY2
bgt $t5, $at, WHILE_BODY2
j WHILE_END3
WHILE_BODY2:
lw $t0, 24($gp)
# getValueReg: src=gp[24] (mem $gp+24) -> $t0 (name=t0)
li $at, 2
rem $t0, $t0, $at
# getValueReg: src=t0 (temp en reg existente) -> $s3
li $at, 0
seq $s3, $s3, $at
# emitCondBranch: raw='t4 > 0' -> left='t4', op='>', right='0', branch_on_true=True
# getValueReg: src=t4 (temp en reg existente) -> $s3
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t4 en $s3, right=0 en $at
# emitCondBranch: emitiendo bgt $s3, $at, IF_THEN4
bgt $s3, $at, IF_THEN4
j IF_ELSE6
IF_THEN4:
# param gp[24]
# call toString n_args=1
lw $t0, 24($gp)
# getValueReg: src=gp[24] (mem $gp+24) -> $t0 (name=gp[24]_tmp)
move $s0, $t0
# call toString: this_reg=$s0 inicializado desde gp[24]
jal toString
# getValueReg: src=t3 (temp en reg existente) -> $v0
# binary t0 := gp[0] + t3 con strings (concat simplificada: dst copia de t3)
# getValueReg: src=t0 (temp en reg existente) -> $v0
# binary t2 := t0 + " es par\n" con strings (concat simplificada: dst copia de t0)
sw $t1, 0($gp)
j IF_END5
IF_ELSE6:
# param gp[24]
# call toString n_args=1
lw $t0, 24($gp)
# getValueReg: src=gp[24] (mem $gp+24) -> $t0 (name=gp[24]_tmp)
move $s0, $t0
# call toString: this_reg=$s0 inicializado desde gp[24]
jal toString
# getValueReg: src=t3 (temp en reg existente) -> $v0
# binary t0 := gp[0] + t3 con strings (concat simplificada: dst copia de t3)
# getValueReg: src=t0 (temp en reg existente) -> $v0
# binary t2 := t0 + " es impar\n" con strings (concat simplificada: dst copia de t0)
sw $t1, 0($gp)
IF_END5:
lw $t0, 24($gp)
# getValueReg: src=gp[24] (mem $gp+24) -> $t0 (name=t0)
li $at, 1
add $t0, $t0, $at
sw $t0, 24($gp)
j WHILE_START1
WHILE_END3:
# getValueReg: src=gp -> $gp
li $t5, 16
# index_load: idx inmediato 16 -> $t5
addu $t6, $gp, $t5
lw $t0, 0($t6)
li $t0, 8
# ERROR: temp t6 usado sin valor inicial
# index_load t5 := t6[t8] (base no soportada)
# ERROR: temp t5 usado sin valor inicial
li $at, 2
# binary t0 := t5 * 2 (no soportado)
li $t0, 3
# getValueReg: src=3 (imm) -> $t0 (name=3)
li $t0, 5
# getValueReg: src=5 (imm) -> $t0 (name=t2)
li $at, 3
sub $t0, $t0, $at
# getValueReg: src=t2 (temp en reg existente) -> $v1
li $at, 2
div $v1, $v1, $at
# getValueReg: src=t0 (temp en reg existente) -> $t4
# binary t1 := t0 + t1 con strings (concat simplificada: dst copia de t0)
sw $t4, 28($gp)
lw $t0, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t0 (name=t1)
# binary t1 := gp[0] + "Resultado de la expresión: " con strings (concat simplificada: dst copia de gp[0])
# param gp[28]
# call toString n_args=1
lw $t0, 28($gp)
# getValueReg: src=gp[28] (mem $gp+28) -> $t0 (name=gp[28]_tmp)
move $s0, $t0
# call toString: this_reg=$s0 inicializado desde gp[28]
jal toString
# getValueReg: src=t1 (temp en reg existente) -> $v1
# binary t0 := t1 + t3 con strings (concat simplificada: dst copia de t1)
# getValueReg: src=t0 (temp en reg existente) -> $v1
# binary t2 := t0 + "\n" con strings (concat simplificada: dst copia de t0)
sw $t1, 0($gp)
li $t0, 0
sw $t0, 32($gp)
# param gp[16]
# param 90
# param 85
# param 95
# call Estudiante_promedioNotas n_args=4
lw $t0, 16($gp)
# getValueReg: src=gp[16] (mem $gp+16) -> $t0 (name=gp[16]_tmp)
move $s0, $t0
# call Estudiante_promedioNotas: this_reg=$s0 inicializado desde gp[16]
li $t0, 90
# getValueReg: src=90 (imm) -> $t0 (name=90)
addiu $sp, $sp, -4
sw $t0, 0($sp)
li $t0, 85
# getValueReg: src=85 (imm) -> $t0 (name=85)
addiu $sp, $sp, -4
sw $t0, 0($sp)
li $t0, 95
# getValueReg: src=95 (imm) -> $t0 (name=95)
addiu $sp, $sp, -4
sw $t0, 0($sp)
jal Estudiante_promedioNotas
addiu $sp, $sp, 12
sw $v0, 32($gp)
lw $t0, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t0 (name=t0)
# binary t0 := gp[0] + "Promedio (entero): " con strings (concat simplificada: dst copia de gp[0])
# param gp[32]
# call toString n_args=1
lw $t0, 32($gp)
# getValueReg: src=gp[32] (mem $gp+32) -> $t0 (name=gp[32]_tmp)
move $s0, $t0
# call toString: this_reg=$s0 inicializado desde gp[32]
jal toString
# getValueReg: src=t0 (temp en reg existente) -> $t3
# binary t1 := t0 + t3 con strings (concat simplificada: dst copia de t0)
# getValueReg: src=t1 (temp en reg existente) -> $s5
# binary t2 := t1 + "\n" con strings (concat simplificada: dst copia de t1)
sw $t1, 0($gp)
# fin de main (toplevel)
li $v0, 10
syscall
