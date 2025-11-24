; Compiscript TAC
; program: 20251124-111543_btest6.cps
; generated: 2025-11-24T11:15:43

FUNCTION factorial:
	t0 := fp[8] == 0
	IF t0 > 0 GOTO IF_THEN1
	GOTO IF_ELSE3
IF_THEN1:
	RETURN 1
IF_ELSE3:
	t1 := fp[8] - 1
	PARAM t1
	CALL factorial, 1
	t2 := R
	t1 := fp[8] * t2
	RETURN t1
END FUNCTION factorial

FUNCTION main:
	fp[4] := 0
WHILE_START4:
	t0 := fp[4] < 10
	IF t0 > 0 GOTO WHILE_BODY5
	GOTO WHILE_END6
WHILE_BODY5:
	t0 := fp[4] != 5
	IF t0 > 0 GOTO IF_THEN7
	GOTO IF_END8
IF_THEN7:
	PARAM fp[4]
	CALL factorial, 1
	t1 := R
	fp[0] := t1
IF_END8:
	t2 := fp[4] + 1
	fp[4] := t2
	GOTO WHILE_START4
WHILE_END6:
END FUNCTION main

