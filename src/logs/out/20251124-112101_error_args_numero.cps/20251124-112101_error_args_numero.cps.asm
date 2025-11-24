# mips generado por compiscript
# program: 20251124-112101_error_args_numero.cps

.data
__gp_base: .space 256

.text
.globl main
f:
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
la $gp, __gp_base
# param 1
# call f n_args=1
li $t2, 1
# getValueReg: src=1 (imm) -> $t2 (name=1)
move $s0, $t2
# call f: this_reg=$s0 inicializado desde 1
jal f
sw $v0, 0($gp)
# param 1
# param 2
# param 3
# call f n_args=3
li $t3, 1
# getValueReg: src=1 (imm) -> $t3 (name=1)
move $s0, $t3
# call f: this_reg=$s0 inicializado desde 1
li $t4, 2
# getValueReg: src=2 (imm) -> $t4 (name=2)
addiu $sp, $sp, -4
sw $t4, 0($sp)
li $t5, 3
# getValueReg: src=3 (imm) -> $t5 (name=3)
addiu $sp, $sp, -4
sw $t5, 0($sp)
jal f
addiu $sp, $sp, 8
sw $v0, 4($gp)
# fin de main (toplevel)
li $v0, 10
syscall
