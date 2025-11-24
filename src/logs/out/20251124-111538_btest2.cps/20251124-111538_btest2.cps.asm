# mips generado por compiscript
# program: 20251124-111538_btest2.cps

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
li $t0, 1
# assign a slot protegido fp[0] (old fp/ra), se ignora
lw $t1, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $t1 (name=fp[12]_tmp)
lw $t2, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t2 (name=t0)
mul $t2, $t2, $t1
# getValueReg: src=t0 (temp en reg existente) -> $t2
lw $t3, 4($fp)
# getValueReg: src=fp[4] (mem $fp+4) -> $t3 (name=t0)
add $t3, $t3, $t2
# assign a slot protegido fp[0] (old fp/ra), se ignora
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
