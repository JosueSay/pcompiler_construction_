# mips generado por compiscript
# program: 20251124-112105_success_params_y_return.cps

.data
__gp_base: .space 256

.text
.globl main
suma:
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
# param 2
# param 3
# call suma n_args=2
li $t2, 2
# getValueReg: src=2 (imm) -> $t2 (name=2)
move $s0, $t2
# call suma: this_reg=$s0 inicializado desde 2
li $t3, 3
# getValueReg: src=3 (imm) -> $t3 (name=3)
addiu $sp, $sp, -4
sw $t3, 0($sp)
jal suma
addiu $sp, $sp, 4
sw $v0, 0($gp)
# fin de main (toplevel)
li $v0, 10
syscall
