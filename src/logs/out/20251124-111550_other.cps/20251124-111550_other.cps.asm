# mips generado por compiscript
# program: 20251124-111550_other.cps

.data
__gp_base: .space 256

.text
.globl main
main:
la $gp, __gp_base
li $t0, 0
# getValueReg: src=gp -> $gp
# getValueReg: src=t1 (temp en reg existente) -> $t0
move $t5, $t0
addu $t6, $gp, $t5
li $t1, 5
# getValueReg: src=5 (imm) -> $t1 (name=5)
sw $t1, 0($t6)
li $t2, 4
# getValueReg: src=gp -> $gp
# getValueReg: src=t0 (temp en reg existente) -> $t0
move $t5, $t0
addu $t6, $gp, $t5
# getValueReg: src=factorial no soportado explícitamente -> devuelve None
# index_store gp[t0] := factorial (src no soportado)
# fin de main (toplevel)
li $v0, 10
syscall
