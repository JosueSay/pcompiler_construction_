# mips generado por compiscript
# program: 20251124-112605_for_azucar_while.cps

.data
__gp_base: .space 256

.text
.globl main
main:
la $gp, __gp_base
li $t0, 0
sw $t0, 0($gp)
li $t1, 0
sw $t1, 4($gp)
FOR_START1:
lw $t2, 4($gp)
# getValueReg: src=gp[4] (mem $gp+4) -> $t2 (name=t0)
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
lw $t3, 4($gp)
# getValueReg: src=gp[4] (mem $gp+4) -> $t3 (name=gp[4]_tmp)
lw $t4, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t4 (name=t1)
add $t4, $t4, $t3
sw $t4, 0($gp)
j FOR_START1
FOR_END3:
# fin de main (toplevel)
li $v0, 10
syscall
