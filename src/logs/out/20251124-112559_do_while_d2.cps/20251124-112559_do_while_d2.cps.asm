# mips generado por compiscript
# program: 20251124-112559_do_while_d2.cps

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
DO_BODY1:
lw $t1, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t1 (name=t0)
li $at, 1
sub $t1, $t1, $at
# assign a slot protegido fp[0] (old fp/ra), se ignora
DO_COND2:
lw $t2, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t2 (name=t1)
li $at, 0
sgt $t2, $t2, $at
# emitCondBranch: raw='t1 > 0' -> left='t1', op='>', right='0', branch_on_true=True
# getValueReg: src=t1 (temp en reg existente) -> $t2
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t1 en $t2, right=0 en $at
# emitCondBranch: emitiendo bgt $t2, $at, DO_BODY1
bgt $t2, $at, DO_BODY1
j DO_END3
DO_END3:
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
