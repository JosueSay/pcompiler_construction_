# mips generado por compiscript
# program: 20251124-112156_error_codigo_muerto_return.cps

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
li $t0, 1
# getValueReg: src=1 (imm) -> $t0 (name=1)
move $v0, $t0
# return 1 -> $v0
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
# call f n_args=0
jal f
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
