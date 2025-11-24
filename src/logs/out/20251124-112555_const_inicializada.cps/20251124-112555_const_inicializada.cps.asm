# mips generado por compiscript
# program: 20251124-112555_const_inicializada.cps

.data
__gp_base: .space 256

.text
.globl main
main:
la $gp, __gp_base
li $t0, 10
# assign destino K no soportado, valor en $t0
lw $t1, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t1 (name=t0)
li $at, 5
add $t1, $t1, $at
sw $t1, 4($gp)
# fin de main (toplevel)
li $v0, 10
syscall
