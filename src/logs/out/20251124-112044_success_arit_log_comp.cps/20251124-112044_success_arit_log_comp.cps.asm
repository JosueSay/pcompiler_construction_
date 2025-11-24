# mips generado por compiscript
# program: 20251124-112044_success_arit_log_comp.cps

.data
__gp_base: .space 256
__str_0: .asciiz "a"

.text
.globl main
main:
la $gp, __gp_base
li $t0, 3
# getValueReg: src=3 (imm) -> $t0 (name=3)
li $t1, 2
# getValueReg: src=2 (imm) -> $t1 (name=t0)
mul $t1, $t1, $t0
# getValueReg: src=t0 (temp en reg existente) -> $t1
li $t2, 1
# getValueReg: src=1 (imm) -> $t2 (name=t0)
add $t2, $t2, $t1
sw $t1, 0($gp)
li $t3, 4
# getValueReg: src=4 (imm) -> $t3 (name=4)
li $t4, 10
# getValueReg: src=10 (imm) -> $t4 (name=t0)
sub $t4, $t4, $t3
# getValueReg: src=t0 (temp en reg existente) -> $t4
li $at, 2
div $t4, $t4, $at
sw $t4, 4($gp)
li $t5, 3
# getValueReg: src=3 (imm) -> $t5 (name=3)
li $t6, 7
# getValueReg: src=7 (imm) -> $t6 (name=t1)
rem $t6, $t6, $t5
sw $t4, 8($gp)
li $t7, 10
sw $t7, 12($gp)
li $t8, 20
sw $t8, 16($gp)
lw $t9, 16($gp)
# getValueReg: src=gp[16] (mem $gp+16) -> $t9 (name=gp[16]_tmp)
lw $s1, 12($gp)
# getValueReg: src=gp[12] (mem $gp+12) -> $s1 (name=t2)
slt $s1, $s1, $t9
sw $s1, 20($gp)
lw $s2, 12($gp)
# getValueReg: src=gp[12] (mem $gp+12) -> $s2 (name=t2)
li $at, 20
sle $s2, $s2, $at
lw $s3, 16($gp)
# getValueReg: src=gp[16] (mem $gp+16) -> $s3 (name=t3)
li $at, 10
sge $s3, $s3, $at
# getValueReg: src=t3 (temp en reg existente) -> $s3
# getValueReg: src=t2 (temp en reg existente) -> $s2
# operador binario '&&' no soportado
sw $s3, 21($gp)
lw $s4, 12($gp)
# getValueReg: src=gp[12] (mem $gp+12) -> $s4 (name=t3)
li $at, 10
seq $s4, $s4, $at
sw $s3, 22($gp)
# assign gp[23] := true (no soportado aún)
# assign gp[24] := false (no soportado aún)
# quad no manejado: unary
# getValueReg: src=t3 (temp en reg existente) -> $s4
lw $s5, 23($gp)
# getValueReg: src=gp[23] (mem $gp+23) -> $s5 (name=t3)
# operador binario '&&' no soportado
lw $s6, 16($gp)
# getValueReg: src=gp[16] (mem $gp+16) -> $s6 (name=gp[16]_tmp)
lw $s7, 12($gp)
# getValueReg: src=gp[12] (mem $gp+12) -> $s7 (name=t2)
slt $s7, $s7, $s6
# getValueReg: src=t2 (temp en reg existente) -> $s7
# getValueReg: src=t3 (temp en reg existente) -> $s5
# operador binario '||' no soportado
sw $s1, 25($gp)
la $v0, __str_0
# getValueReg: src="a" (string) -> $v0 (label=__str_0, name=t1)
# binary t1 := "a" + "b" con strings (concat simplificada: dst copia de "a")
sw $t4, 26($gp)
# fin de main (toplevel)
li $v0, 10
syscall
