# mips generado por compiscript
# program: 20251124-112601_expresiones_puras.cps

.data
__gp_base: .space 256

.text
.globl main
main:
la $gp, __gp_base
li $t0, 2
sw $t0, 0($gp)
li $t1, 3
sw $t1, 4($gp)
lw $t2, 4($gp)
# getValueReg: src=gp[4] (mem $gp+4) -> $t2 (name=gp[4]_tmp)
lw $t3, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t3 (name=t0)
add $t3, $t3, $t2
lw $t4, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t4 (name=t1)
li $at, 1
sub $t4, $t4, $at
# getValueReg: src=t1 (temp en reg existente) -> $t4
# getValueReg: src=t0 (temp en reg existente) -> $t3
mul $t3, $t3, $t4
sw $t3, 8($gp)
# fin de main (toplevel)
li $v0, 10
syscall
