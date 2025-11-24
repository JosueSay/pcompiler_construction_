# mips generado por compiscript
# program: 20251124-112609_funcion_con_parametros_y_return.cps

.data
__gp_base: .space 256

.text
.globl main
add:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
lw $t0, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $t0 (name=fp[12]_tmp)
lw $t1, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t1 (name=t0)
add $t1, $t1, $t0
# getValueReg: src=t0 (temp en reg existente) -> $t1
move $v0, $t1
# return t0 -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
main:
la $gp, __gp_base
li $t2, 4
sw $t2, 0($gp)
li $t3, 7
sw $t3, 4($gp)
# param gp[0]
# param gp[4]
# call add n_args=2
lw $t4, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t4 (name=gp[0]_tmp)
move $s0, $t4
# call add: this_reg=$s0 inicializado desde gp[0]
lw $t5, 4($gp)
# getValueReg: src=gp[4] (mem $gp+4) -> $t5 (name=gp[4]_tmp)
addiu $sp, $sp, -4
sw $t5, 0($sp)
jal add
addiu $sp, $sp, 4
sw $v0, 8($gp)
# fin de main (toplevel)
li $v0, 10
syscall
