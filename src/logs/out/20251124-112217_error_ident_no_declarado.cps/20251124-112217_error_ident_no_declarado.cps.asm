# mips generado por compiscript
# program: 20251124-112217_error_ident_no_declarado.cps

.data
__gp_base: .space 256

.text
.globl main
main:
la $gp, __gp_base
li $t0, 1
sw $t0, 0($gp)
lw $t1, 0($gp)
# assign destino b no soportado, valor en $t1
# fin de main (toplevel)
li $v0, 10
syscall
