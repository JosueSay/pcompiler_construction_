# mips generado por compiscript
# program: 20251124-111536_btest0.cps

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
# prologo frame_size=16
la $gp, __gp_base
# init $gp con base de globals (__gp_base)
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
lw $t2, 4($fp)
# getValueReg: src=fp[4] (mem $fp+4) -> $t2 (name=fp[4]_tmp)
lw $t3, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t3 (name=t0)
mul $t3, $t3, $t2
# getValueReg: src=t0 (temp en reg existente) -> $t3
lw $t4, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t4 (name=t0)
add $t4, $t4, $t3
sw $t1, 8($fp)
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
