# mips generado por compiscript
# program: 20251124-112042_error_op_logico_no_boolean.cps

.data
__gp_base: .space 256
__str_0: .asciiz "s"

.text
.globl main
main:
la $gp, __gp_base
li $t0, 1
sw $t0, 0($gp)
la $t1, __str_0
# assign literal string "s" -> $t1 (label=__str_0)
sw $t1, 4($gp)
# getValueReg: src=true no soportado explícitamente -> devuelve None
lw $t2, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t2 (name=t0)
# binary t0 := gp[0] && true (no soportado)
sw $t2, 12($gp)
# getValueReg: src=false no soportado explícitamente -> devuelve None
lw $t3, 4($gp)
# getValueReg: src=gp[4] (mem $gp+4) -> $t3 (name=t0)
# binary t0 := gp[4] || false (no soportado)
sw $t2, 13($gp)
# quad no manejado: unary
sw $t2, 14($gp)
# fin de main (toplevel)
li $v0, 10
syscall
