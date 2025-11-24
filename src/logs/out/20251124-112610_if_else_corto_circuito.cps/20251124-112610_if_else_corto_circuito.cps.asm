# mips generado por compiscript
# program: 20251124-112610_if_else_corto_circuito.cps

.data
__gp_base: .space 256

.text
.globl main
main:
la $gp, __gp_base
li $t0, 5
sw $t0, 0($gp)
li $t1, 10
sw $t1, 4($gp)
lw $t2, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t2 (name=t0)
li $at, 3
slt $t2, $t2, $at
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t2
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t2, right=0 en $at
# emitCondBranch: emitiendo bgt $t2, $at, IF_THEN1
bgt $t2, $at, IF_THEN1
j Lor4
Lor4:
lw $t3, 4($gp)
# getValueReg: src=gp[4] (mem $gp+4) -> $t3 (name=t0)
li $at, 7
sgt $t3, $t3, $at
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t3
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t3, right=0 en $at
# emitCondBranch: emitiendo bgt $t3, $at, Land5
bgt $t3, $at, Land5
j IF_ELSE3
Land5:
lw $t4, 4($gp)
# getValueReg: src=gp[4] (mem $gp+4) -> $t4 (name=gp[4]_tmp)
lw $t5, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t5 (name=t0)
sne $t5, $t5, $t4
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t5
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t5, right=0 en $at
# emitCondBranch: emitiendo bgt $t5, $at, IF_THEN1
bgt $t5, $at, IF_THEN1
j IF_ELSE3
IF_THEN1:
li $t6, 0
sw $t6, 0($gp)
j IF_END2
IF_ELSE3:
li $t7, 1
sw $t7, 0($gp)
IF_END2:
# fin de main (toplevel)
li $v0, 10
syscall
