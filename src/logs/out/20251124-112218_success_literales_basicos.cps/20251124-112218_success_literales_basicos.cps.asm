# mips generado por compiscript
# program: 20251124-112218_success_literales_basicos.cps

.data
__gp_base: .space 256
__str_0: .asciiz "hola"

.text
.globl main
main:
la $gp, __gp_base
li $t0, 123
sw $t0, 0($gp)
la $t1, __str_0
# assign literal string "hola" -> $t1 (label=__str_0)
sw $t1, 4($gp)
# assign gp[12] := false (no soportado aún)
# assign gp[13] := [1,2,3] (no soportado aún)
# assign gp[21] := null (no soportado aún)
# fin de main (toplevel)
li $v0, 10
syscall
