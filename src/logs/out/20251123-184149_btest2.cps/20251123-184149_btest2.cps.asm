.data
str_0: .asciiz ""
str_1: .asciiz "rojo"
str_2: .asciiz "Hola, mi nombre es "
str_3: .asciiz "Ahora tengo "
str_4: .asciiz " años."
str_5: .asciiz " está estudiando en "
str_6: .asciiz " grado."
str_7: .asciiz "Erick"
str_8: .asciiz "\n"
str_9: .asciiz " es par\n"
str_10: .asciiz " es impar\n"
str_11: .asciiz "Resultado de la expresión: "
str_12: .asciiz "Promedio (entero): "

.text
.globl main

toString:
addi $sp, $sp, -4
sw $ra, 0($sp)
addi $sp, $sp, -4
sw $fp, 0($sp)
move $fp, $sp
addi $sp, $sp, -256
lw $t8, 8($fp)
sw $t8, -4($fp)
la $v0, str_0
j toString_end
toString_end:
move $sp, $fp
lw $fp, 0($sp)
addi $sp, $sp, 4
lw $ra, 0($sp)
addi $sp, $sp, 4
jr $ra
Persona_constructor:
addi $sp, $sp, -4
sw $ra, 0($sp)
addi $sp, $sp, -4
sw $fp, 0($sp)
move $fp, $sp
addi $sp, $sp, -256
lw $t8, 16($fp)
sw $t8, -4($fp)
lw $t8, 12($fp)
sw $t8, -8($fp)
lw $t8, 8($fp)
sw $t8, -12($fp)
lw $t8, -4($fp)
lw $t9, -8($fp)
sw $t9, 4($t8)
lw $t8, -4($fp)
lw $t9, -12($fp)
sw $t9, 8($t8)
lw $t8, -4($fp)
la $t9, str_1
sw $t9, 12($t8)
Persona_constructor_end:
move $sp, $fp
lw $fp, 0($sp)
addi $sp, $sp, 4
lw $ra, 0($sp)
addi $sp, $sp, 4
jr $ra
Persona_saludar:
addi $sp, $sp, -4
sw $ra, 0($sp)
addi $sp, $sp, -4
sw $fp, 0($sp)
move $fp, $sp
addi $sp, $sp, -256
lw $t8, 8($fp)
sw $t8, -4($fp)
lw $t8, -4($fp)
lw $t9, 4($t8)
sw $t9, -8($fp)
la $t8, str_2
lw $t9, -8($fp)
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -12($fp)
lw $v0, -12($fp)
j Persona_saludar_end
Persona_saludar_end:
move $sp, $fp
lw $fp, 0($sp)
addi $sp, $sp, 4
lw $ra, 0($sp)
addi $sp, $sp, 4
jr $ra
Persona_incrementarEdad:
addi $sp, $sp, -4
sw $ra, 0($sp)
addi $sp, $sp, -4
sw $fp, 0($sp)
move $fp, $sp
addi $sp, $sp, -256
lw $t8, 12($fp)
sw $t8, -4($fp)
lw $t8, 8($fp)
sw $t8, -8($fp)
lw $t8, -4($fp)
lw $t9, 8($t8)
sw $t9, -12($fp)
lw $t8, -12($fp)
lw $t9, -8($fp)
add $t8, $t8, $t9
sw $t8, -16($fp)
lw $t8, -4($fp)
lw $t9, -16($fp)
sw $t9, 8($t8)
lw $t8, -4($fp)
lw $t9, 8($t8)
sw $t9, -12($fp)
lw $t8, -12($fp)
addi $sp, $sp, -4
sw $t8, 0($sp)
jal toString
sw $v0, -20($fp)
addi $sp, $sp, 4
la $t8, str_3
lw $t9, -20($fp)
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -24($fp)
lw $t8, -24($fp)
la $t9, str_4
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -20($fp)
lw $v0, -20($fp)
j Persona_incrementarEdad_end
Persona_incrementarEdad_end:
move $sp, $fp
lw $fp, 0($sp)
addi $sp, $sp, 4
lw $ra, 0($sp)
addi $sp, $sp, 4
jr $ra
Estudiante_constructor:
addi $sp, $sp, -4
sw $ra, 0($sp)
addi $sp, $sp, -4
sw $fp, 0($sp)
move $fp, $sp
addi $sp, $sp, -256
lw $t8, 20($fp)
sw $t8, -4($fp)
lw $t8, 16($fp)
sw $t8, -8($fp)
lw $t8, 12($fp)
sw $t8, -12($fp)
lw $t8, 8($fp)
sw $t8, -16($fp)
lw $t8, -4($fp)
lw $t9, -8($fp)
sw $t9, 4($t8)
lw $t8, -4($fp)
lw $t9, -12($fp)
sw $t9, 8($t8)
lw $t8, -4($fp)
la $t9, str_1
sw $t9, 12($t8)
lw $t8, -4($fp)
lw $t9, -16($fp)
sw $t9, 16($t8)
Estudiante_constructor_end:
move $sp, $fp
lw $fp, 0($sp)
addi $sp, $sp, 4
lw $ra, 0($sp)
addi $sp, $sp, 4
jr $ra
Estudiante_estudiar:
addi $sp, $sp, -4
sw $ra, 0($sp)
addi $sp, $sp, -4
sw $fp, 0($sp)
move $fp, $sp
addi $sp, $sp, -256
lw $t8, 8($fp)
sw $t8, -4($fp)
lw $t8, -4($fp)
lw $t9, 4($t8)
sw $t9, -8($fp)
lw $t8, -8($fp)
la $t9, str_5
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -12($fp)
lw $t8, -4($fp)
lw $t9, 16($t8)
sw $t9, -16($fp)
lw $t8, -16($fp)
addi $sp, $sp, -4
sw $t8, 0($sp)
jal toString
sw $v0, -8($fp)
addi $sp, $sp, 4
lw $t8, -12($fp)
lw $t9, -8($fp)
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -20($fp)
lw $t8, -20($fp)
la $t9, str_6
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -12($fp)
lw $v0, -12($fp)
j Estudiante_estudiar_end
Estudiante_estudiar_end:
move $sp, $fp
lw $fp, 0($sp)
addi $sp, $sp, 4
lw $ra, 0($sp)
addi $sp, $sp, 4
jr $ra
Estudiante_promedioNotas:
addi $sp, $sp, -4
sw $ra, 0($sp)
addi $sp, $sp, -4
sw $fp, 0($sp)
move $fp, $sp
addi $sp, $sp, -256
lw $t8, 20($fp)
sw $t8, -4($fp)
lw $t8, 16($fp)
sw $t8, -8($fp)
lw $t8, 12($fp)
sw $t8, -12($fp)
lw $t8, 8($fp)
sw $t8, -16($fp)
lw $t8, -8($fp)
lw $t9, -12($fp)
add $t8, $t8, $t9
sw $t8, -20($fp)
lw $t8, -20($fp)
lw $t9, -16($fp)
add $t8, $t8, $t9
sw $t8, -24($fp)
lw $t8, -24($fp)
li $t9, 3
div $t8, $t9
mflo $t8
sw $t8, -20($fp)
lw $t8, -20($fp)
sw $t8, -28($fp)
lw $v0, -28($fp)
j Estudiante_promedioNotas_end
Estudiante_promedioNotas_end:
move $sp, $fp
lw $fp, 0($sp)
addi $sp, $sp, 4
lw $ra, 0($sp)
addi $sp, $sp, 4
jr $ra
main:
move $fp, $sp
addi $sp, $sp, -256
la $t8, str_0
sw $t8, -4($fp)
la $t8, str_7
sw $t8, -8($fp)
li $a0, 20
li $v0, 9
syscall
sw $zero, 0($v0)
la $t7, str_0
sw $t7, 4($v0)
sw $zero, 8($v0)
la $t7, str_0
sw $t7, 12($v0)
sw $zero, 16($v0)
sw $v0, -12($fp)
lw $t8, -12($fp)
addi $sp, $sp, -4
sw $t8, 0($sp)
lw $t8, -8($fp)
addi $sp, $sp, -4
sw $t8, 0($sp)
li $t8, 20
addi $sp, $sp, -4
sw $t8, 0($sp)
li $t8, 3
addi $sp, $sp, -4
sw $t8, 0($sp)
jal Estudiante_constructor
sw $v0, -16($fp)
addi $sp, $sp, 16
lw $t8, -12($fp)
sw $t8, -20($fp)
lw $t8, -20($fp)
addi $sp, $sp, -4
sw $t8, 0($sp)
jal Persona_saludar
sw $v0, -24($fp)
addi $sp, $sp, 4
lw $t8, -4($fp)
lw $t9, -24($fp)
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -28($fp)
lw $t8, -28($fp)
la $t9, str_8
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -32($fp)
lw $t8, -32($fp)
sw $t8, -4($fp)
lw $t8, -20($fp)
addi $sp, $sp, -4
sw $t8, 0($sp)
jal Estudiante_estudiar
sw $v0, -24($fp)
addi $sp, $sp, 4
lw $t8, -4($fp)
lw $t9, -24($fp)
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -28($fp)
lw $t8, -28($fp)
la $t9, str_8
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -32($fp)
lw $t8, -32($fp)
sw $t8, -4($fp)
lw $t8, -20($fp)
addi $sp, $sp, -4
sw $t8, 0($sp)
li $t8, 5
addi $sp, $sp, -4
sw $t8, 0($sp)
jal Persona_incrementarEdad
sw $v0, -24($fp)
addi $sp, $sp, 8
lw $t8, -4($fp)
lw $t9, -24($fp)
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -28($fp)
lw $t8, -28($fp)
la $t9, str_8
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -32($fp)
lw $t8, -32($fp)
sw $t8, -4($fp)
li $t8, 1
sw $t8, -36($fp)
L19:
lw $t8, -36($fp)
li $t9, 5
sle $t8, $t8, $t9
sw $t8, -40($fp)
lw $t8, -40($fp)
beqz $t8, LE20
lw $t8, -36($fp)
li $t9, 2
div $t8, $t9
mfhi $t8
sw $t8, -44($fp)
lw $t8, -44($fp)
li $t9, 0
seq $t8, $t8, $t9
sw $t8, -48($fp)
lw $t8, -48($fp)
beqz $t8, ML1
lw $t8, -36($fp)
addi $sp, $sp, -4
sw $t8, 0($sp)
jal toString
sw $v0, -24($fp)
addi $sp, $sp, 4
lw $t8, -4($fp)
lw $t9, -24($fp)
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -28($fp)
lw $t8, -28($fp)
la $t9, str_9
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -32($fp)
lw $t8, -32($fp)
sw $t8, -4($fp)
j ML2
ML1:
lw $t8, -36($fp)
addi $sp, $sp, -4
sw $t8, 0($sp)
jal toString
sw $v0, -24($fp)
addi $sp, $sp, 4
lw $t8, -4($fp)
lw $t9, -24($fp)
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -28($fp)
lw $t8, -28($fp)
la $t9, str_10
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -32($fp)
lw $t8, -32($fp)
sw $t8, -4($fp)
ML2:
lw $t8, -36($fp)
li $t9, 1
add $t8, $t8, $t9
sw $t8, -52($fp)
lw $t8, -52($fp)
sw $t8, -36($fp)
LC21:
j L19
LE20:
lw $t8, -20($fp)
lw $t9, 8($t8)
sw $t9, -44($fp)
lw $t8, -44($fp)
li $t9, 2
mul $t8, $t8, $t9
sw $t8, -52($fp)
li $t8, 5
li $t9, 3
sub $t8, $t8, $t9
sw $t8, -44($fp)
lw $t8, -44($fp)
li $t9, 2
div $t8, $t9
mflo $t8
sw $t8, -56($fp)
lw $t8, -52($fp)
lw $t9, -56($fp)
add $t8, $t8, $t9
sw $t8, -44($fp)
lw $t8, -44($fp)
sw $t8, -60($fp)
lw $t8, -4($fp)
la $t9, str_11
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -24($fp)
lw $t8, -60($fp)
addi $sp, $sp, -4
sw $t8, 0($sp)
jal toString
sw $v0, -28($fp)
addi $sp, $sp, 4
lw $t8, -24($fp)
lw $t9, -28($fp)
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -32($fp)
lw $t8, -32($fp)
la $t9, str_8
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -24($fp)
lw $t8, -24($fp)
sw $t8, -4($fp)
li $t8, 0
sw $t8, -64($fp)
lw $t8, -20($fp)
addi $sp, $sp, -4
sw $t8, 0($sp)
li $t8, 90
addi $sp, $sp, -4
sw $t8, 0($sp)
li $t8, 85
addi $sp, $sp, -4
sw $t8, 0($sp)
li $t8, 95
addi $sp, $sp, -4
sw $t8, 0($sp)
jal Estudiante_promedioNotas
sw $v0, -52($fp)
addi $sp, $sp, 16
lw $t8, -52($fp)
sw $t8, -64($fp)
lw $t8, -4($fp)
la $t9, str_12
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -28($fp)
lw $t8, -64($fp)
addi $sp, $sp, -4
sw $t8, 0($sp)
jal toString
sw $v0, -32($fp)
addi $sp, $sp, 4
lw $t8, -28($fp)
lw $t9, -32($fp)
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -24($fp)
lw $t8, -24($fp)
la $t9, str_8
move $a0, $t8
move $a1, $t9
jal __concat
sw $v0, -28($fp)
lw $t8, -28($fp)
sw $t8, -4($fp)
li $v0, 10
syscall
__concat:
move $t0, $a0
move $t1, $a1
move $t4, $t0
li $t2, 0
__concat_len1:
lb $t7, 0($t4)
beq $t7, $zero, __concat_len1_done
addi $t2, $t2, 1
addi $t4, $t4, 1
j __concat_len1
__concat_len1_done:
move $t4, $t1
li $t3, 0
__concat_len2:
lb $t7, 0($t4)
beq $t7, $zero, __concat_len2_done
addi $t3, $t3, 1
addi $t4, $t4, 1
j __concat_len2
__concat_len2_done:
add $t5, $t2, $t3
addi $t5, $t5, 1
move $a0, $t5
li $v0, 9
syscall
move $t6, $v0
move $t4, $t0
__concat_copy1:
lb $t7, 0($t4)
beq $t7, $zero, __concat_copy2_start
sb $t7, 0($t6)
addi $t4, $t4, 1
addi $t6, $t6, 1
j __concat_copy1
__concat_copy2_start:
move $t4, $t1
__concat_copy2:
lb $t7, 0($t4)
beq $t7, $zero, __concat_done
sb $t7, 0($t6)
addi $t4, $t4, 1
addi $t6, $t6, 1
j __concat_copy2
__concat_done:
sb $zero, 0($t6)
jr $ra

    li $v0, 10
    syscall
