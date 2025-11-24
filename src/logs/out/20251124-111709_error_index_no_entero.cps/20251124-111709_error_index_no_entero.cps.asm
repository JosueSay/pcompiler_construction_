# mips generado por compiscript
# program: 20251124-111709_error_index_no_entero.cps

.data
__gp_base: .space 256
__str_0: .asciiz "0"

.text
.globl main
main:
la $gp, __gp_base
# assign gp[0] := [10,20,30] (no soportado aún)
# quad no manejado: len
# emitCondBranch: raw='"0"<0' -> left='"0"', op='<', right='0', branch_on_true=True
la $t0, __str_0
# getValueReg: src="0" (string) -> $t0 (label=__str_0, name=__str_0)
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left="0" en $t0, right=0 en $at
# emitCondBranch: emitiendo blt $t0, $at, oob1
blt $t0, $at, oob1
# emitCondBranch: raw='"0">=t1' -> left='"0"', op='>=', right='t1', branch_on_true=True
la $t1, __str_0
# getValueReg: src="0" (string) -> $t1 (label=__str_0, name=__str_0)
# ERROR: temp t1 usado sin valor inicial
# emitCondBranch: regs -> left="0" en $t1, right=t1 en None
# branch sobre '"0">=t1' no soportado (operandos)
j ok2
oob1:
# call __bounds_error n_args=0
jal __bounds_error
ok2:
lw $t6, 0($gp)
la $t2, __str_0
# getValueReg: src="0" (string) -> $t2 (label=__str_0, name=__str_0)
move $t5, $t2
addu $t6, $t6, $t5
lw $t3, 0($t6)
sw $t3, 8($gp)
# quad no manejado: len
# emitCondBranch: raw='true<0' -> left='true', op='<', right='0', branch_on_true=True
# getValueReg: src=true no soportado explícitamente -> devuelve None
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=true en None, right=0 en $at
# branch sobre 'true<0' no soportado (operandos)
# emitCondBranch: raw='true>=t1' -> left='true', op='>=', right='t1', branch_on_true=True
# getValueReg: src=true no soportado explícitamente -> devuelve None
# ERROR: temp t1 usado sin valor inicial
# emitCondBranch: regs -> left=true en None, right=t1 en None
# branch sobre 'true>=t1' no soportado (operandos)
j ok4
oob3:
# call __bounds_error n_args=0
jal __bounds_error
ok4:
lw $t6, 0($gp)
# getValueReg: src=true no soportado explícitamente -> devuelve None
# index_load t0 := gp[0][true] (idx sin valor)
sw $t3, 12($gp)
# fin de main (toplevel)
li $v0, 10
syscall
