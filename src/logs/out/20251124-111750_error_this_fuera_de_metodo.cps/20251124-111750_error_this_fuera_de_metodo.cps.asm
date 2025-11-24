# mips generado por compiscript
# program: 20251124-111750_error_this_fuera_de_metodo.cps

.data
__gp_base: .space 256

.text
.globl main
f:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
# quad no manejado: field_store
li $t0, 0
# getValueReg: src=0 (imm) -> $t0 (name=0)
move $v0, $t0
# return 0 -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
