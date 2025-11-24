# mips generado por compiscript
# program: 20251123-183150_btest9.cps

.data
__gp_base: .space 256

.text
.globl main

# -------------------------
# main wrapper (ADDED)
# -------------------------
# Initializes $gp and $s0 (your generator expects $s0 as 'this'),
# then calls Program_main and exits.
main:
    # initialize global pointer (used by your code: gp[...])
    la   $gp, __gp_base

    # initialize 'this' register expected by your generator
    li   $s0, 0

    # call program entry
    jal  Program_main

    # exit cleanly
    li   $v0, 10
    syscall

# -------------------------
# Generated procedures follow
# -------------------------
Program_InputInt:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $t0, 8
# getValueReg: src=t2 (temp en reg existente) -> $t0
move $t5, $t0
addu $t6, $s0, $t5
lw $t1, 0($t6)
li $t2, 0
# getValueReg: src=t0 (temp en reg existente) -> $t1
# getValueReg: src=t3 (temp en reg existente) -> $t2
move $t5, $t2
addu $t6, $t1, $t5
lw $t3, 0($t6)
# getValueReg: src=t2 (temp en reg existente) -> $t3
move $v0, $t3
# return t2 -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra

Program_OutputInt:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra

Program_ReturnNumber:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
li $t4, 8
# getValueReg: src=t2 (temp en reg existente) -> $t4
move $t5, $t4
addu $t6, $s0, $t5
lw $t5, 0($t6)
li $t6, 0
# getValueReg: src=t0 (temp en reg existente) -> $t5
# getValueReg: src=t3 (temp en reg existente) -> $t6
move $t5, $t6
addu $t6, $t5, $t5
lw $t7, 0($t6)
# getValueReg: src=t2 (temp en reg existente) -> $t7
move $v0, $t7
# return t2 -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra

Program_factorial:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
# getValueReg: acceso fp[16] fuera de frame_size=16, se permite la carga (advertencia)
lw $t8, 16($fp)
# getValueReg: src=fp[16] (mem $fp+16) -> $t8 (name=t0)
li $at, 0
seq $t8, $t8, $at
# emitCondBranch: raw='t0 > 0' -> left='t0', op='>', right='0', branch_on_true=True
# getValueReg: src=t0 (temp en reg existente) -> $t8
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t0 en $t8, right=0 en $at
# emitCondBranch: emitiendo bgt $t8, $at, IF_THEN1
bgt $t8, $at, IF_THEN1
j IF_ELSE3
IF_THEN1:
li $t9, 1
# getValueReg: src=1 (imm) -> $t9 (name=1)
move $v0, $t9
# return 1 -> $v0
IF_ELSE3:
# getValueReg: acceso fp[16] fuera de frame_size=16, se permite la carga (advertencia)
lw $s1, 16($fp)
# getValueReg: src=fp[16] (mem $fp+16) -> $s1 (name=t1)
li $at, 1
sub $s1, $s1, $at
# param this
# param t1
# call Program_factorial n_args=2
# getValueReg: src=this -> $s0
move $s0, $s0
# call Program_factorial: this_reg=$s0 inicializado desde this
# getValueReg: src=t1 (temp en reg existente) -> $s1
addiu $sp, $sp, -4
sw $s1, 0($sp)
jal Program_factorial
addiu $sp, $sp, 4
# getValueReg: src=t2 (temp en reg existente) -> $v0
# getValueReg: acceso fp[16] fuera de frame_size=16, se permite la carga (advertencia)
lw $s2, 16($fp)
# getValueReg: src=fp[16] (mem $fp+16) -> $s2 (name=t1)
mul $s2, $s2, $v0
# getValueReg: src=t1 (temp en reg existente) -> $s2
move $v0, $s2
# return t1 -> $v0
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra

Program_main:
# prologo frame_size=16
addiu $sp, $sp, -16
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# this_reg=$s0 definido pero sin this_param_offset en frame; se asume que el caller inicializa 'this'
# assign fp[0] := [newB(),newB(),newB(),newB(),newB()] (no soportado aún)
li $s3, 0
sw $s3, 8($fp)
li $s4, 0
sw $s4, 12($fp)
li $s5, 8
# getValueReg: src=t1 (temp en reg existente) -> $s2
move $t5, $s2
addu $t6, $s0, $t5
li $s6, 3
# getValueReg: src=3 (imm) -> $s6 (name=3)
sw $s6, 0($t6)
WHILE_START4:
lw $s7, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $s7 (name=t2)
li $at, 10
sle $s7, $s7, $at
# emitCondBranch: raw='t2 > 0' -> left='t2', op='>', right='0', branch_on_true=True
# getValueReg: src=t2 (temp en reg existente) -> $v0
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t2 en $v0, right=0 en $at
# emitCondBranch: emitiendo bgt $v0, $at, WHILE_BODY5
bgt $v0, $at, WHILE_BODY5
j WHILE_END6
WHILE_BODY5:
# quad no manejado: field_store
# quad no manejado: len
# emitCondBranch: raw='fp[12]<0' -> left='fp[12]', op='<', right='0', branch_on_true=True
lw $v1, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $v1 (name=fp[12]_tmp)
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=fp[12] en $v1, right=0 en $at
# emitCondBranch: emitiendo blt $v1, $at, oob9
blt $v1, $at, oob9
# emitCondBranch: raw='fp[12]>=t1' -> left='fp[12]', op='>=', right='t1', branch_on_true=True
lw $t0, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $t0 (name=fp[12]_tmp)
# getValueReg: src=t1 (temp en reg existente) -> $s2
# emitCondBranch: regs -> left=fp[12] en $t0, right=t1 en $s2
# emitCondBranch: emitiendo bge $t0, $s2, oob9
bge $t0, $s2, oob9
j ok10
oob9:
# call __bounds_error n_args=0
jal __bounds_error
ok10:
lw $t6, 0($fp)
lw $t0, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $t0 (name=fp[12]_tmp)
move $t5, $t0
addu $t6, $t6, $t5
lw $t0, 0($t6)
li $t9, 0
# getValueReg: src=t3 (temp en reg existente) -> $t6
# getValueReg: src=t0 (temp en reg existente) -> $s5
move $t5, $s5
addu $t6, $t6, $t5
lw $s3, 0($t6)
# quad no manejado: len
# emitCondBranch: raw='0<0' -> left='0', op='<', right='0', branch_on_true=True
li $t0, 0
# getValueReg: src=0 (imm) -> $t0 (name=0)
li $t0, 0
# getValueReg: src=0 (imm) -> $t0 (name=0)
# emitCondBranch: regs -> left=0 en $t0, right=0 en $t0
# emitCondBranch: emitiendo blt $t0, $t0, oob11
blt $t0, $t0, oob11
# emitCondBranch: raw='0>=t1' -> left='0', op='>=', right='t1', branch_on_true=True
li $t0, 0
# getValueReg: src=0 (imm) -> $t0 (name=0)
# getValueReg: src=t1 (temp en reg existente) -> $s2
# emitCondBranch: regs -> left=0 en $t0, right=t1 en $s2
# emitCondBranch: emitiendo bge $t0, $s2, oob11
bge $t0, $s2, oob11
j ok12
oob11:
# call __bounds_error n_args=0
jal __bounds_error
ok12:
# getValueReg: src=t4 (temp en reg existente) -> $s3
li $t5, 0
# index_load: idx inmediato 0 -> $t5
addu $t6, $s3, $t5
lw $t0, 0($t6)
# getValueReg: src=t0 (temp en reg existente) -> $s5
li $at, 5
seq $s5, $s5, $at
# emitCondBranch: raw='t2 > 0' -> left='t2', op='>', right='0', branch_on_true=True
# getValueReg: src=t2 (temp en reg existente) -> $v0
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=t2 en $v0, right=0 en $at
# emitCondBranch: emitiendo bgt $v0, $at, IF_THEN7
bgt $v0, $at, IF_THEN7
j IF_END8
IF_THEN7:
# quad no manejado: field_store
# param this
# call Program_ReturnNumber n_args=1
# getValueReg: src=this -> $s0
move $s0, $s0
# call Program_ReturnNumber: this_reg=$s0 inicializado desde this
jal Program_ReturnNumber
# param this
# param t0
# call Program_factorial n_args=2
# getValueReg: src=this -> $s0
move $s0, $s0
# call Program_factorial: this_reg=$s0 inicializado desde this
# getValueReg: src=t0 (temp en reg existente) -> $v0
addiu $sp, $sp, -4
sw $v0, 0($sp)
jal Program_factorial
addiu $sp, $sp, 4
sw $t9, 16($fp)
# param this
# param fp[16]
# call Program_OutputInt n_args=2
# getValueReg: src=this -> $s0
move $s0, $s0
# call Program_OutputInt: this_reg=$s0 inicializado desde this
# getValueReg: acceso fp[16] fuera de frame_size=16, se permite la carga (advertencia)
lw $t0, 16($fp)
# getValueReg: src=fp[16] (mem $fp+16) -> $t0 (name=fp[16]_tmp)
addiu $sp, $sp, -4
sw $t0, 0($sp)
jal Program_OutputInt
addiu $sp, $sp, 4
IF_END8:
# quad no manejado: len
# emitCondBranch: raw='fp[12]<0' -> left='fp[12]', op='<', right='0', branch_on_true=True
lw $t0, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $t0 (name=fp[12]_tmp)
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=fp[12] en $t0, right=0 en $at
# emitCondBranch: emitiendo blt $t0, $at, oob13
blt $t0, $at, oob13
# emitCondBranch: raw='fp[12]>=t1' -> left='fp[12]', op='>=', right='t1', branch_on_true=True
lw $t0, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $t0 (name=fp[12]_tmp)
# getValueReg: src=t1 (temp en reg existente) -> $v0
# emitCondBranch: regs -> left=fp[12] en $t0, right=t1 en $v0
# emitCondBranch: emitiendo bge $t0, $v0, oob13
bge $t0, $v0, oob13
j ok14
oob13:
# call __bounds_error n_args=0
jal __bounds_error
ok14:
lw $t6, 0($fp)
lw $t0, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $t0 (name=fp[12]_tmp)
move $t5, $t0
addu $t6, $t6, $t5
lw $t0, 0($t6)
li $s4, 0
# getValueReg: src=t4 (temp en reg existente) -> $s3
# getValueReg: src=t0 (temp en reg existente) -> $t9
move $t5, $t9
addu $t6, $s3, $t5
lw $s6, 0($t6)
# quad no manejado: len
# emitCondBranch: raw='0<0' -> left='0', op='<', right='0', branch_on_true=True
li $t0, 0
# getValueReg: src=0 (imm) -> $t0 (name=0)
li $t0, 0
# getValueReg: src=0 (imm) -> $t0 (name=0)
# emitCondBranch: regs -> left=0 en $t0, right=0 en $t0
# emitCondBranch: emitiendo blt $t0, $t0, oob15
blt $t0, $t0, oob15
# emitCondBranch: raw='0>=t1' -> left='0', op='>=', right='t1', branch_on_true=True
li $t0, 0
# getValueReg: src=0 (imm) -> $t0 (name=0)
# getValueReg: src=t1 (temp en reg existente) -> $v0
# emitCondBranch: regs -> left=0 en $t0, right=t1 en $v0
# emitCondBranch: emitiendo bge $t0, $v0, oob15
bge $t0, $v0, oob15
j ok16
oob15:
# call __bounds_error n_args=0
jal __bounds_error
ok16:
# getValueReg: src=t3 (temp en reg existente) -> $s6
li $t5, 0
# index_load: idx inmediato 0 -> $t5
addu $t6, $s6, $t5
lw $t0, 0($t6)
# param this
# param t0
# call Program_factorial n_args=2
# getValueReg: src=this -> $s0
move $s0, $s0
# call Program_factorial: this_reg=$s0 inicializado desde this
# getValueReg: src=t0 (temp en reg existente) -> $t9
addiu $sp, $sp, -4
sw $t9, 0($sp)
jal Program_factorial
addiu $sp, $sp, 4
# quad no manejado: len
# emitCondBranch: raw='fp[12]<0' -> left='fp[12]', op='<', right='0', branch_on_true=True
lw $t0, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $t0 (name=fp[12]_tmp)
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=fp[12] en $t0, right=0 en $at
# emitCondBranch: emitiendo blt $t0, $at, oob17
blt $t0, $at, oob17
# emitCondBranch: raw='fp[12]>=t5' -> left='fp[12]', op='>=', right='t5', branch_on_true=True
lw $t0, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $t0 (name=fp[12]_tmp)
# ERROR: temp t5 usado sin valor inicial
# emitCondBranch: regs -> left=fp[12] en $t0, right=t5 en None
# branch sobre 'fp[12]>=t5' no soportado (operandos)
j ok18
oob17:
# call __bounds_error n_args=0
jal __bounds_error
ok18:
lw $t6, 0($fp)
lw $t0, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $t0 (name=fp[12]_tmp)
move $t5, $t0
addu $t6, $t6, $t5
lw $t0, 0($t6)
li $v1, 8
# getValueReg: src=t3 (temp en reg existente) -> $s6
# getValueReg: src=t6 (temp en reg existente) -> $v1
move $t5, $v1
addu $t6, $s6, $t5
# getValueReg: src=t1 (temp en reg existente) -> $v0
sw $v0, 0($t6)
# quad no manejado: len
# emitCondBranch: raw='fp[12]<0' -> left='fp[12]', op='<', right='0', branch_on_true=True
lw $t0, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $t0 (name=fp[12]_tmp)
# emitCondBranch: right inmediato 0 -> $at (no pisa left)
li $at, 0
# emitCondBranch: regs -> left=fp[12] en $t0, right=0 en $at
# emitCondBranch: emitiendo blt $t0, $at, oob19
blt $t0, $at, oob19
# emitCondBranch: raw='fp[12]>=t1' -> left='fp[12]', op='>=', right='t1', branch_on_true=True
lw $t0, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $t0 (name=fp[12]_tmp)
# getValueReg: src=t1 (temp en reg existente) -> $v0
# emitCondBranch: regs -> left=fp[12] en $t0, right=t1 en $v0
# emitCondBranch: emitiendo bge $t0, $v0, oob19
bge $t0, $v0, oob19
j ok20
oob19:
# call __bounds_error n_args=0
jal __bounds_error
ok20:
lw $t6, 0($fp)
lw $t0, 12($fp)
# getValueReg: src=fp[12] (mem $fp+12) -> $t0 (name=fp[12]_tmp)
move $t5, $t0
addu $t6, $t6, $t5
lw $t0, 0($t6)
li $t0, 8
# getValueReg: src=t3 (temp en reg existente) -> $s6
# getValueReg: src=t0 (temp en reg existente) -> $t9
move $t5, $t9
addu $t6, $s6, $t5
lw $t0, 0($t6)
li $t0, 0
# getValueReg: src=t4 (temp en reg existente) -> $s3
# getValueReg: src=t6 (temp en reg existente) -> $v1
move $t5, $v1
addu $t6, $s3, $t5
lw $t0, 0($t6)
# param this
# param t0
# call Program_OutputInt n_args=2
# getValueReg: src=this -> $s0
move $s0, $s0
# call Program_OutputInt: this_reg=$s0 inicializado desde this
# getValueReg: src=t0 (temp en reg existente) -> $t9
addiu $sp, $sp, -4
sw $t9, 0($sp)
jal Program_OutputInt
addiu $sp, $sp, 4
lw $t0, 8($fp)
# getValueReg: src=fp[8] (mem $fp+8) -> $t0 (name=t7)
li $at, 1
add $t0, $t0, $at
sw $t0, 8($fp)
j WHILE_START4
WHILE_END6:
# epilogo
move $sp, $fp
lw $ra, 4($sp)
lw $fp, 0($sp)
addiu $sp, $sp, 16
jr $ra

#############################################
# RUNTIME FUNCTION: __bounds_error
# Prints error and exits
#############################################

        .data
__bounds_error_msg: .asciiz "Runtime error: array index out of bounds\n"

        .text
__bounds_error:
        # Print error message
        li  $v0, 4
        la  $a0, __bounds_error_msg
        syscall

        # Exit program
        li  $v0, 10
        syscall

