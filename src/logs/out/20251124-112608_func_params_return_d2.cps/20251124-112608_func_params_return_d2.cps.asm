# mips generado por compiscript
# program: 20251124-112608_func_params_return_d2.cps

.data
__gp_base: .space 256

.text
.globl main
add:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
lw $t0, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $t0 (name=fp[12]_tmp)
lw $t1, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t1 (name=t0)
add $t1, $t1, $t0
# getValueReg: src=t0 (temp en reg existente) -> $t1
move $v0, $t1
# return t0 -> $v0
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
li $t2, 4
# assign a slot protegido fp[0] (old fp/ra), se ignora
li $t3, 7
# assign a slot protegido fp[4] (old fp/ra), se ignora
lw $t4, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t4 (name=t0)
li $at, 1
add $t4, $t4, $at
# param t0
# param fp[4]
# call add n_args=2
# getValueReg: src=t0 (temp en reg existente) -> $t4
move $s0, $t4
# call add: this_reg=$s0 inicializado desde t0
lw $t5, 4($fp)
# getValueReg: src=fp[4] (mem $fp+4) -> $t5 (name=fp[4]_tmp)
addiu $sp, $sp, -4
sw $t5, 0($sp)
jal add
addiu $sp, $sp, 4
sw $v0, 8($fp)
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
