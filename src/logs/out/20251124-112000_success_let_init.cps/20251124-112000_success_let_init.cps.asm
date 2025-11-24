# mips generado por compiscript
# program: 20251124-112000_success_let_init.cps

.data
__gp_base: .space 256
__str_0: .asciiz "hola"

.text
.globl main
main:
la $gp, __gp_base
li $t0, 1
sw $t0, 0($gp)
la $t1, __str_0
# assign literal string "hola" -> $t1 (label=__str_0)
sw $t1, 4($gp)
# assign gp[12] := true (no soportado aún)
# assign gp[13] := [1,2] (no soportado aún)
li $t2, 2
sw $t2, 0($gp)
# fin de main (toplevel)
li $v0, 10
syscall
