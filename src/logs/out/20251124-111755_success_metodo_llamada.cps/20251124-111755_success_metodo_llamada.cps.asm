# mips generado por compiscript
# program: 20251124-111755_success_metodo_llamada.cps

.data
__gp_base: .space 256

.text
.globl main
Mathy_suma:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
# getValueReg: acceso fp[20] fuera de frame_size=16, se permite la carga (advertencia)
lw $t0, 20($fp)
# getValueReg: src=fp[20] (mem $fp+20) -> $t0 (name=fp[20]_tmp)
# getValueReg: acceso fp[16] fuera de frame_size=16, se permite la carga (advertencia)
lw $t1, 16($fp)
# getValueReg: src=fp[16] (mem $fp+16) -> $t1 (name=t0)
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
# newobj t1 = newobj Mathy, size=0
li $a0, 0
li $v0, 9
syscall
# newobj: puntero -> temp t1 en $v0
sw $v0, 0($gp)
# param gp[0]
# param 2
# param 3
# call Mathy_suma n_args=3
lw $t2, 0($gp)
# getValueReg: src=gp[0] (mem $gp+0) -> $t2 (name=gp[0]_tmp)
move $s0, $t2
# call Mathy_suma: this_reg=$s0 inicializado desde gp[0]
li $t3, 2
# getValueReg: src=2 (imm) -> $t3 (name=2)
addiu $sp, $sp, -4
sw $t3, 0($sp)
li $t4, 3
# getValueReg: src=3 (imm) -> $t4 (name=3)
addiu $sp, $sp, -4
sw $t4, 0($sp)
jal Mathy_suma
addiu $sp, $sp, 8
sw $v0, 8($gp)
# fin de main (toplevel)
li $v0, 10
syscall
