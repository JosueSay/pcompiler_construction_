; Compiscript TAC
; program: 20251124-111540_btest3.cps
; generated: 2025-11-24T11:15:40

FUNCTION OutputInt:
END FUNCTION OutputInt

FUNCTION InputInt:
	RETURN 0
END FUNCTION InputInt

FUNCTION fibonacci:
	t0 := fp[8] == 0
	IF t0 > 0 GOTO IF_THEN1
	GOTO IF_ELSE3
IF_THEN1:
	fp[0] := 1
	GOTO IF_END2
IF_ELSE3:
	t0 := fp[8] == 1
	IF t0 > 0 GOTO IF_THEN4
	GOTO IF_ELSE6
IF_THEN4:
	fp[0] := 1
	GOTO IF_END5
IF_ELSE6:
	t1 := fp[8] - 1
	PARAM t1
	CALL fibonacci, 1
	t2 := R
	t1 := fp[8] - 2
	PARAM t1
	CALL fibonacci, 1
	t3 := R
	t1 := t2 + t3
	fp[0] := t1
IF_END5:
IF_END2:
	RETURN fp[0]
END FUNCTION fibonacci

FUNCTION main:
	fp[8] := 0
WHILE_START7:
	t0 := fp[8] <= 20
	IF t0 > 0 GOTO WHILE_BODY8
	GOTO WHILE_END9
WHILE_BODY8:
	PARAM fp[8]
	CALL fibonacci, 1
	t1 := R
	fp[4] := t1
	PARAM fp[4]
	CALL OutputInt, 1
	t2 := fp[8] + 1
	fp[8] := t2
	GOTO WHILE_START7
WHILE_END9:
END FUNCTION main

