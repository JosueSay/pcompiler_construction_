# mips generado por compiscript
# program: 20251124-112606_for_basic_d2.cps

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
li $t0, 0
# assign a slot protegido fp[0] (old fp/ra), se ignora
li $t1, 0
# assign a slot protegido fp[4] (old fp/ra), se ignora
FOR_START1:
lw $t2, 4($fp)
# getValueReg: src=fp[4] (mem $fp+4) -> $t2 (name=t0)
li $at, 3
slt $t2, $t2, $at
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t2
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t2, right=0 en $at
# emitCondBranch: emitiendo bgt $t2, $at, FOR_BODY2
bgt $t2, $at, FOR_BODY2
j FOR_END3
FOR_BODY2:
lw $t3, 4($fp)
# getValueReg: src=fp[4] (mem $fp+4) -> $t3 (name=fp[4]_tmp)
lw $t4, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t4 (name=t1)
add $t4, $t4, $t3
# assign a slot protegido fp[0] (old fp/ra), se ignora
j FOR_START1
FOR_END3:
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
