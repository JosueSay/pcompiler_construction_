# mips generado por compiscript
# program: 20251124-111710_error_literal_heterogeneo.cps

.data
__gp_base: .space 256

.text
.globl main
main:
la $gp, __gp_base
# assign gp[0] := [1,"dos"] (no soportado aún)
# fin de main (toplevel)
li $v0, 10
syscall
