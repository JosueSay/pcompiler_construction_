# mips generado por compiscript
# program: 20251124-112104_error_return_tipo.cps

.data
__gp_base: .space 256

.text
.globl main
h:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
# getValueReg: src=true no soportado explícitamente -> devuelve None
# return true (no soportado aún, $v0 sin cambiar)
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra
