# mips generado por compiscript
# program: 20251124-112538_acceso_propiedad_lectura_y_escritura.cps

.data
__gp_base: .space 256

.text
.globl main
main:
la $gp, __gp_base
# newobj t0 = newobj P, size=8
li $a0, 8
li $v0, 9
syscall
# newobj: puntero -> temp t0 en $v0
sw $v0, 0($gp)
li $t0, 0
# getValueReg: src=gp -> $gp
# getValueReg: src=t2 (temp en reg existente) -> $t0
move $t5, $t0
addu $t6, $gp, $t5
li $t1, 1
# getValueReg: src=1 (imm) -> $t1 (name=1)
sw $t1, 0($t6)
# getValueReg: src=gp -> $gp
li $t5, 0
# index_load: idx inmediato 0 -> $t5
addu $t6, $gp, $t5
lw $t2, 0($t6)
li $t3, 0
# getValueReg: src=t3 (temp en reg existente) -> $t2
# getValueReg: src=t4 (temp en reg existente) -> $t3
move $t5, $t3
addu $t6, $t2, $t5
lw $t4, 0($t6)
# getValueReg: src=gp -> $gp
li $t5, 0
# index_load: idx inmediato 0 -> $t5
addu $t6, $gp, $t5
lw $t5, 0($t6)
li $t6, 4
# getValueReg: src=t5 (temp en reg existente) -> $t5
# getValueReg: src=t6 (temp en reg existente) -> $t6
move $t5, $t6
addu $t6, $t5, $t5
lw $t7, 0($t6)
# getValueReg: src=t4 (temp en reg existente) -> $t7
# getValueReg: src=t2 (temp en reg existente) -> $t4
add $t4, $t4, $t7
sw $t4, 8($gp)
# fin de main (toplevel)
li $v0, 10
syscall
