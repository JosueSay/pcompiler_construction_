# mips generado por compiscript
# program: 20251124-112239_success_decl_simple.cps

.data
__gp_base: .space 256
__str_0: .asciiz "x"

.text
.globl main
main:
la $gp, __gp_base
li $t0, 1
sw $t0, 0($gp)
la $t1, __str_0
# assign literal string "x" -> $t1 (label=__str_0)
sw $t1, 4($gp)
# assign gp[12] := true (no soportado aún)
# fin de main (toplevel)
li $v0, 10
syscall
