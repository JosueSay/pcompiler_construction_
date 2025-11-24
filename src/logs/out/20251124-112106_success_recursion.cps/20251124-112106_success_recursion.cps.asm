# mips generado por compiscript
# program: 20251124-112106_success_recursion.cps

.data
__gp_base: .space 256

.text
.globl main
fact:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
lw $t0, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t0 (name=t0)
li $at, 1
sle $t0, $t0, $at
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t0
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t0, right=0 en $at
# emitCondBranch: emitiendo bgt $t0, $at, IF_THEN1
bgt $t0, $at, IF_THEN1
j IF_END2
IF_THEN1:
li $t1, 1
# getValueReg: src=1 (imm) -> $t1 (name=1)
move $v0, $t1
# return 1 -> $v0
IF_END2:
lw $t2, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t2 (name=t1)
li $at, 1
sub $t2, $t2, $at
# param t1
# call fact n_args=1
# getValueReg: src=t1 (temp en reg existente) -> $t2
move $s0, $t2
# call fact: this_reg=$s0 inicializado desde t1
jal fact
# getValueReg: src=t2 (temp en reg existente) -> $v0
lw $t3, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t3 (name=t1)
mul $t3, $t3, $v0
# getValueReg: src=t1 (temp en reg existente) -> $t3
move $v0, $t3
# return t1 -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
main:
la $gp, __gp_base
# param 5
# call fact n_args=1
li $t4, 5
# getValueReg: src=5 (imm) -> $t4 (name=5)
move $s0, $t4
# call fact: this_reg=$s0 inicializado desde 5
jal fact
sw $v0, 0($gp)
# fin de main (toplevel)
li $v0, 10
syscall
