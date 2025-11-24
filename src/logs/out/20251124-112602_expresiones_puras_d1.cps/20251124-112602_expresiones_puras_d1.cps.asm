# mips generado por compiscript
# program: 20251124-112602_expresiones_puras_d1.cps

.data
__gp_base: .space 256

.text
.globl main
main:
# prologo frame_size=16
la $gp, __gp_base
# init $gp con base de globals (__gp_base)
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $t0, 2
# assign a slot protegido fp[0] (old fp/ra), se ignora
li $t1, 3
# assign a slot protegido fp[4] (old fp/ra), se ignora
li $t2, 4
sw $t2, 8($fp)
lw $t3, 4($fp)
# getValueReg: src=fp[4] (mem $fp+4) -> $t3 (name=fp[4]_tmp)
lw $t4, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t4 (name=t0)
add $t4, $t4, $t3
lw $t5, 4($fp)
# getValueReg: src=fp[4] (mem $fp+4) -> $t5 (name=fp[4]_tmp)
lw $t6, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t6 (name=t1)
sub $t6, $t6, $t5
# getValueReg: src=t1 (temp en reg existente) -> $t6
# getValueReg: src=t0 (temp en reg existente) -> $t4
mul $t4, $t4, $t6
sw $t4, 12($fp)
lw $t7, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $t7 (name=t2)
li $at, 10
slt $t7, $t7, $at
lw $t8, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $t8 (name=t3)
li $at, 20
sgt $t8, $t8, $at
lw $t9, 4($fp)
# getValueReg: src=fp[4] (mem $fp+4) -> $t9 (name=fp[4]_tmp)
lw $s1, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $s1 (name=t4)
sne $s1, $s1, $t9
# getValueReg: src=t4 (temp en reg existente) -> $s1
# getValueReg: src=t3 (temp en reg existente) -> $t8
# operador binario '&&' no soportado
# getValueReg: src=t4 (temp en reg existente) -> $s1
# getValueReg: src=t2 (temp en reg existente) -> $t7
# operador binario '||' no soportado
sw $s1, 16($fp)
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
