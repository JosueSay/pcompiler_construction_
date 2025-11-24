; Compiscript TAC
; program: 20251124-111546_btest8.cps
; generated: 2025-11-24T11:15:46

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
	t0 := 0
	t1 := t0
	fp[t1] := 5
	t1 := 4
	t0 := t1
	fp[t0] := 6
END FUNCTION main

