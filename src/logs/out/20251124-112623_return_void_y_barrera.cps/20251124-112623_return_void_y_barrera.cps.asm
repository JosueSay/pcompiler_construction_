# mips generado por compiscript
# program: 20251124-112623_return_void_y_barrera.cps

.data
__gp_base: .space 256

.text
.globl main
logTwice:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
# return (sin valor)
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
main:
la $gp, __gp_base
li $t0, 8
sw $t0, 0($gp)
# param gp[0]
# call logTwice n_args=1
lw $t1, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t1 (name=gp[0]_tmp)
move $s0, $t1
# call logTwice: this_reg=$s0 inicializado desde gp[0]
jal logTwice
# fin de main (toplevel)
li $v0, 10
syscall
