# mips generado por compiscript
# program: 20251124-112041_error_aritmica_no_numerica.cps

.data
__gp_base: .space 256
__str_0: .asciiz "hola"
__str_1: .asciiz "b"
__str_2: .asciiz "a"

.text
.globl main
main:
la $gp, __gp_base
# getValueReg: src=true no soportado explícitamente -> devuelve None
li $t0, 1
# getValueReg: src=1 (imm) -> $t0 (name=t0)
# binary t0 := 1 + true (no soportado)
sw $t0, 0($gp)
la $t1, __str_0
# getValueReg: src="hola" (string) -> $t1 (label=__str_0, name=t0)
li $at, 2
mul $t1, $t1, $at
sw $t0, 4($gp)
la $t2, __str_1
# getValueReg: src="b" (string) -> $t2 (label=__str_1, name=__str_1)
la $t3, __str_2
# getValueReg: src="a" (string) -> $t3 (label=__str_2, name=t0)
sub $t3, $t3, $t2
sw $t0, 8($gp)
# fin de main (toplevel)
li $v0, 10
syscall
