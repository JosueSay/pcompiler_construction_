# mips generado por compiscript
# program: 20251124-112618_obb_ge_len.cps

.data
__gp_base: .space 256

.text
.globl main
main:
# prologo frame_size=16
la $gp, __gp_base
# init $gp con base de globals (__gp_base)
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
# assign fp[0] := [1,2,3] (no soportado aún)
li $t0, 3
sw $t0, 8($fp)
# quad no manejado: len
# emitCondBranch: raw='fp[8]<0' -> left='fp[8]', op='<', right='0', branch_on_true=True
lw $t1, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t1 (name=fp[8]_tmp)
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=fp[8] en $t1, right=0 en $at
# emitCondBranch: emitiendo blt $t1, $at, oob1
blt $t1, $at, oob1
# emitCondBranch: raw='fp[8]>=t1' -> left='fp[8]', op='>=', right='t1', branch_on_true=True
lw $t2, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t2 (name=fp[8]_tmp)
# ERROR: temp t1 usado sin valor inicial
# emitCondBranch: regs -> left=fp[8] en $t2, right=t1 en None
# branch sobre 'fp[8]>=t1' no soportado (operandos)
j ok2
oob1:
# call __bounds_error n_args=0
jal __bounds_error
ok2:
lw $t6, 0($fp)
lw $t3, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t3 (name=fp[8]_tmp)
move $t5, $t3
addu $t6, $t6, $t5
lw $t4, 0($t6)
sw $t4, 12($fp)
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
