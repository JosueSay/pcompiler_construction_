# mips generado por compiscript
# program: 20251124-112104_success_closure_captura.cps

.data
__gp_base: .space 256

.text
.globl main
mk:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $t0, 10
# assign a slot protegido fp[0] (old fp/ra), se ignora
add:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
lw $t1, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t1 (name=fp[8]_tmp)
lw $t2, 0($fp)
# getValueReg: src=fp[0] (mem $fp+0) -> $t2 (name=t0)
add $t2, $t2, $t1
# getValueReg: src=t0 (temp en reg existente) -> $t2
move $v0, $t2
# return t0 -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
main:
la $gp, __gp_base
# quad no manejado: mkenv
# quad no manejado: mkclos
# param 5
# quad no manejado: callc
# getValueReg: src=t3 (temp en reg existente) -> $v0
# return t3 -> $v0
# epilogo sin frame (noop)
# call mk n_args=0 (warning: pending_params=1)
li $t3, 5
# getValueReg: src=5 (imm) -> $t3 (name=5)
addiu $sp, $sp, -4
sw $t3, 0($sp)
jal mk
addiu $sp, $sp, 4
sw $v0, 0($gp)
# fin de main (toplevel)
li $v0, 10
syscall
