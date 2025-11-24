# mips generado por compiscript
# program: 20251124-112556_const_y_let_d1.cps

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
li $t0, 5
# assign destino k no soportado, valor en $t0
lw $t1, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t1 (name=t0)
li $at, 1
add $t1, $t1, $at
# assign a slot protegido fp[4] (old fp/ra), se ignora
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
