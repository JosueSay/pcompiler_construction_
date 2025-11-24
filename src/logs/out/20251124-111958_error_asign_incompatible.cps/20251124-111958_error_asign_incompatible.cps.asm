# mips generado por compiscript
# program: 20251124-111958_error_asign_incompatible.cps

.data
__gp_base: .space 256
__str_0: .asciiz "hola"

.text
.globl main
main:
la $gp, __gp_base
la $t0, __str_0
# assign literal string "hola" -> $t0 (label=__str_0)
sw $t0, 0($gp)
# fin de main (toplevel)
li $v0, 10
syscall
