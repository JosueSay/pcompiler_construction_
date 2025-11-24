# mips generado por compiscript
# program: 20251124-112550_class_test_v10.cps

.data
__gp_base: .space 256

.text
.globl main
Box_constructor:
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
# getValueReg: src=[7,8,9] no soportado explícitamente -> devuelve None
# index_store this[t1] := [7,8,9] (src no soportado)
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
Box_get:
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
# quad no manejado: len
# emitCondBranch: raw='fp[16]<0' -> left='fp[16]', op='<', right='0', branch_on_true=True
# getValueReg: acceso fp[16] fuera de frame_size=16, se permite la carga (advertencia)
lw $t3, 16($fp)
# getValueReg: src=fp[16] (mem $fp+16) -> $t3 (name=fp[16]_tmp)
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=fp[16] en $t3, right=0 en $at
# emitCondBranch: emitiendo blt $t3, $at, oob1
blt $t3, $at, oob1
# emitCondBranch: raw='fp[16]>=t1' -> left='fp[16]', op='>=', right='t1', branch_on_true=True
# getValueReg: acceso fp[16] fuera de frame_size=16, se permite la carga (advertencia)
lw $t4, 16($fp)
# getValueReg: src=fp[16] (mem $fp+16) -> $t4 (name=fp[16]_tmp)
# getValueReg: src=t1 (temp en reg existente) -> $t1
# emitCondBranch: regs -> left=fp[16] en $t4, right=t1 en $t1
# emitCondBranch: emitiendo bge $t4, $t1, oob1
bge $t4, $t1, oob1
j ok2
oob1:
# call __bounds_error n_args=0
jal __bounds_error
ok2:
# getValueReg: src=t0 (temp en reg existente) -> $t2
# getValueReg: acceso fp[16] fuera de frame_size=16, se permite la carga (advertencia)
lw $t5, 16($fp)
# getValueReg: src=fp[16] (mem $fp+16) -> $t5 (name=fp[16]_tmp)
addu $t6, $t2, $t5
lw $t6, 0($t6)
# getValueReg: src=t2 (temp en reg existente) -> $t6
move $v0, $t6
# return t2 -> $v0
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
# newobj t0 = newobj Box, size=8
li $a0, 8
li $v0, 9
syscall
# newobj: puntero -> temp t0 en $v0
# param t0
# call Box_constructor n_args=1
# getValueReg: src=t0 (temp en reg existente) -> $v0
move $s0, $v0
# call Box_constructor: this_reg=$s0 inicializado desde t0
jal Box_constructor
# assign a slot protegido fp[0] (old fp/ra), se ignora
# param fp[0]
# param 1
# call Box_get n_args=2
lw $t7, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t7 (name=fp[0]_tmp)
move $s0, $t7
# call Box_get: this_reg=$s0 inicializado desde fp[0]
li $t8, 1
# getValueReg: src=1 (imm) -> $t8 (name=1)
addiu $sp, $sp, -4
sw $t8, 0($sp)
jal Box_get
addiu $sp, $sp, 4
sw $t1, 8($fp)
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
