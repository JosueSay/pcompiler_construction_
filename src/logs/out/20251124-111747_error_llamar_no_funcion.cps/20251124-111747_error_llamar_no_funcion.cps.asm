# mips generado por compiscript
# program: 20251124-111747_error_llamar_no_funcion.cps

.data
__gp_base: .space 256

.text
.globl main
main:
la $gp, __gp_base
li $t0, 1
sw $t0, 0($gp)
# call gp[0] n_args=0
jal gp[0]
# fin de main (toplevel)
li $v0, 10
syscall
