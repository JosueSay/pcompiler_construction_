# mips generado por compiscript
# program: 20251124-111548_debug_program.cps

.data
__gp_base: .space 256
__str_0: .asciiz "hola"
__str_1: .asciiz "Hola "
__str_2: .asciiz "num"
__str_3: .asciiz "A"
__str_4: .asciiz "B"
__str_5: .asciiz ""

.text
.globl main
main:
la $gp, __gp_base
li $t0, 1
sw $t0, 0($gp)
la $t1, __str_0
# assign literal string "hola" -> $t1 (label=__str_0)
sw $t1, 4($gp)
# assign gp[12] := true (no soportado aún)
la $t2, __str_1
# getValueReg: src="Hola " (string) -> $t2 (label=__str_1, name=t0)
# binary t0 := "Hola " + "mundo" con strings (concat simplificada: dst copia de "Hola ")
sw $t2, 13($gp)
li $t3, 5
sw $t3, 21($gp)
# getValueReg: src=true no soportado explícitamente -> devuelve None
li $t4, 1
# getValueReg: src=1 (imm) -> $t4 (name=t0)
# binary t0 := 1 + true (no soportado)
sw $t2, 25($gp)
li $t5, 2
# getValueReg: src=2 (imm) -> $t5 (name=2)
li $t6, 1
# getValueReg: src=1 (imm) -> $t6 (name=t0)
add $t6, $t6, $t5
sw $t2, 29($gp)
li $t7, 2
# getValueReg: src=2 (imm) -> $t7 (name=2)
li $t8, 1
# getValueReg: src=1 (imm) -> $t8 (name=t1)
slt $t8, $t8, $t7
# getValueReg: src=true no soportado explícitamente -> devuelve None
# getValueReg: src=t1 (temp en reg existente) -> $t8
# binary t2 := t1 && true (no soportado)
# valor de t2 no inicializado en registros
sw $t9, 33($gp)
# assign gp[34] := [1,2,3] (no soportado aún)
li $s1, 1
# quad no manejado: len
# emitCondBranch: raw='t0<0' -> left='t0', op='<', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $s1
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $s1, right=0 en $at
# emitCondBranch: emitiendo blt $s1, $at, oob1
blt $s1, $at, oob1
# emitCondBranch: raw='t0>=t4' -> left='t0', op='>=', right='t4', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $s1
# ERROR: temp t4 usado sin valor inicial
# emitCondBranch: regs -> left=t0 en $s1, right=t4 en None
# branch sobre 't0>=t4' no soportado (operandos)
j ok2
oob1:
# call __bounds_error n_args=0
jal __bounds_error
ok2:
lw $t6, 34($gp)
# getValueReg: src=t0 (temp en reg existente) -> $s1
move $t5, $s1
addu $t6, $t6, $t5
lw $s2, 0($t6)
sw $s2, 42($gp)
suma:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
lw $s3, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $s3 (name=fp[12]_tmp)
lw $s4, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $s4 (name=t0)
add $s4, $s4, $s3
# getValueReg: src=t0 (temp en reg existente) -> $s4
move $v0, $s4
# return t0 -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
# param 2
# param 3
# call suma n_args=2
li $s5, 2
# getValueReg: src=2 (imm) -> $s5 (name=2)
move $s0, $s5
# call suma: this_reg=$s0 inicializado desde 2
li $s6, 3
# getValueReg: src=3 (imm) -> $s6 (name=3)
addiu $sp, $sp, -4
sw $s6, 0($sp)
jal suma
addiu $sp, $sp, 4
sw $t8, 46($gp)
toStringInt:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
la $s7, __str_2
# getValueReg: src="num" (string) -> $s7 (label=__str_2, name=__str_2)
move $v0, $s7
# return "num" -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
h:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $v1, 1
# getValueReg: src=1 (imm) -> $v1 (name=1)
move $v0, $v1
# return 1 -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
mk:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $t0, 10
# assign a slot protegido fp[0] (old fp/ra), se ignora
add:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
lw $t0, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t0 (name=fp[8]_tmp)
lw $t0, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t0 (name=t0)
lw $at, 8($fp)
add $t0, $t0, $at
# getValueReg: src=t0 (temp en reg existente) -> $s4
move $v0, $s4
# return t0 -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
# quad no manejado: mkenv
# quad no manejado: mkclos
# param 5
# quad no manejado: callc
# getValueReg: src=t3 (temp en reg existente) -> $v0
# return t3 -> $v0
# epilogo sin frame (noop)
# call mk n_args=0 (warning: pending_params=1)
li $t0, 5
# getValueReg: src=5 (imm) -> $t0 (name=5)
addiu $sp, $sp, -4
sw $t0, 0($sp)
jal mk
addiu $sp, $sp, 4
sw $s2, 50($gp)
li $t0, 1
sw $t0, 54($gp)
lw $t0, 54($gp)
# getValueReg: src=gp[54] (mem $gp+54) -> $t0 (name=t4)
li $at, 10
slt $t0, $t0, $at
# emitCondBranch: raw='t4 > 0' -> left='t4', op='>', right='0', branch_on_true=True
# getValueReg: src=t4 (temp en reg existente) -> $t0
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t4 en $t0, right=0 en $at
# emitCondBranch: emitiendo bgt $t0, $at, IF_THEN3
bgt $t0, $at, IF_THEN3
j IF_ELSE5
IF_THEN3:
j IF_END4
IF_ELSE5:
IF_END4:
li $t0, 0
sw $t0, 58($gp)
WHILE_START6:
lw $t0, 58($gp)
# getValueReg: src=gp[58] (mem $gp+58) -> $t0 (name=t4)
li $at, 3
slt $t0, $t0, $at
# emitCondBranch: raw='t4 > 0' -> left='t4', op='>', right='0', branch_on_true=True
# getValueReg: src=t4 (temp en reg existente) -> $t0
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t4 en $t0, right=0 en $at
# emitCondBranch: emitiendo bgt $t0, $at, WHILE_BODY7
bgt $t0, $at, WHILE_BODY7
j WHILE_END8
WHILE_BODY7:
lw $t1, 58($gp)
# getValueReg: src=gp[58] (mem $gp+58) -> $t1 (name=t0)
li $at, 1
add $t1, $t1, $at
sw $t1, 58($gp)
j WHILE_START6
WHILE_END8:
li $t0, 2
sw $t0, 62($gp)
# emitCondBranch: raw='gp[62] == 1' -> left='gp[62]', op='==', right='1', branch_on_true=True
lw $t0, 62($gp)
# getValueReg: src=gp[62] (mem $gp+62) -> $t0 (name=gp[62]_tmp)
# emitCondBranch: right inmediato 1 -> $at (no pisa left)
li $at, 1
# emitCondBranch: regs -> left=gp[62] en $t0, right=1 en $at
# emitCondBranch: emitiendo beq $t0, $at, Lcase11
beq $t0, $at, Lcase11
# emitCondBranch: raw='gp[62] == 2' -> left='gp[62]', op='==', right='2', branch_on_true=True
lw $t0, 62($gp)
# getValueReg: src=gp[62] (mem $gp+62) -> $t0 (name=gp[62]_tmp)
# emitCondBranch: right inmediato 2 -> $at (no pisa left)
li $at, 2
# emitCondBranch: regs -> left=gp[62] en $t0, right=2 en $at
# emitCondBranch: emitiendo beq $t0, $at, Lcase12
beq $t0, $at, Lcase12
j Ldef10
Lcase11:
Lcase12:
Ldef10:
Lend9:
A_constructor:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $t0, 0
# getValueReg: src=t1 (temp en reg existente) -> $t8
move $t5, $t8
addu $t6, $s0, $t5
lw $t7, 16($fp)
sw $t7, 0($t6)
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
A_saludar:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
la $t0, __str_3
# getValueReg: src="A" (string) -> $t0 (label=__str_3, name=__str_3)
move $v0, $t0
# return "A" -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
B_constructor:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $t0, 0
# getValueReg: src=t1 (temp en reg existente) -> $t8
move $t5, $t8
addu $t6, $s0, $t5
lw $t7, 16($fp)
sw $t7, 0($t6)
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
B_saludar:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
la $t0, __str_4
# getValueReg: src="B" (string) -> $t0 (label=__str_4, name=__str_4)
move $v0, $t0
# return "B" -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
B_doble:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $t0, 0
# getValueReg: src=t2 (temp en reg existente) -> $t9
move $t5, $t9
addu $t6, $s0, $t5
lw $t3, 0($t6)
li $t5, 0
# getValueReg: src=t3 (temp en reg existente) -> $v0
move $t5, $v0
addu $t6, $s0, $t5
lw $t7, 0($t6)
# getValueReg: src=t0 (temp en reg existente) -> $s4
# binary t4 := t0 + t2 con strings (concat simplificada: dst copia de t0)
# getValueReg: src=t4 (temp en reg existente) -> $s4
move $v0, $s4
# return t4 -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
# newobj t5 = newobj A, size=4
li $a0, 4
li $v0, 9
syscall
# newobj: puntero -> temp t5 en $v0
# param t5
# param 5
# call A_constructor n_args=2
# getValueReg: src=t5 (temp en reg existente) -> $v0
move $s0, $v0
# call A_constructor: this_reg=$s0 inicializado desde t5
li $t0, 5
# getValueReg: src=5 (imm) -> $t0 (name=5)
addiu $sp, $sp, -4
sw $t0, 0($sp)
jal A_constructor
addiu $sp, $sp, 4
sw $v0, 66($gp)
# newobj t5 = newobj B, size=4
li $a0, 4
li $v0, 9
syscall
# newobj: puntero -> temp t5 en $v0
# param t5
# param 7
# call B_constructor n_args=2
# getValueReg: src=t5 (temp en reg existente) -> $v0
move $s0, $v0
# call B_constructor: this_reg=$s0 inicializado desde t5
li $t0, 7
# getValueReg: src=7 (imm) -> $t0 (name=7)
addiu $sp, $sp, -4
sw $t0, 0($sp)
jal B_constructor
addiu $sp, $sp, 4
sw $v0, 74($gp)
# getValueReg: src=gp -> $gp
li $t5, 74
# index_load: idx inmediato 74 -> $t5
addu $t6, $gp, $t5
lw $t0, 0($t6)
li $s3, 0
# getValueReg: src=t6 (temp en reg existente) -> $t0
# getValueReg: src=t3 (temp en reg existente) -> $s2
move $t5, $s2
addu $t6, $t0, $t5
lw $s5, 0($t6)
sw $t1, 82($gp)
# param gp[74]
# call B_saludar n_args=1
lw $t0, 74($gp)
# getValueReg: src=gp[74] (mem $gp+74) -> $t0 (name=gp[74]_tmp)
move $s0, $t0
# call B_saludar: this_reg=$s0 inicializado desde gp[74]
jal B_saludar
sw $v0, 86($gp)
foo:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
la $t0, __str_5
# assign literal string "" -> $t0 (label=__str_5)
sw $t0, 94($gp)
# param gp[82]
# call toStringInt n_args=1
lw $t0, 82($gp)
# getValueReg: src=gp[82] (mem $gp+82) -> $t0 (name=gp[82]_tmp)
move $s0, $t0
# call toStringInt: this_reg=$s0 inicializado desde gp[82]
jal toStringInt
# getValueReg: src=t0 (temp en reg existente) -> $v0
# binary t1 := gp[94] + t0 con strings (concat simplificada: dst copia de t0)
# getValueReg: src=t1 (temp en reg existente) -> $v0
# binary t2 := t1 + gp[86] con strings (concat simplificada: dst copia de t1)
sw $t9, 94($gp)
# fin de main (toplevel)
li $v0, 10
syscall
