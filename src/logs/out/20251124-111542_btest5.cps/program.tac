; Compiscript TAC
; program: 20251124-111542_btest5.cps
; generated: 2025-11-24T11:15:42

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
	t0 := fp[0] * 2
	gp[0] := t0
	PARAM gp[0]
	CALL factorial, 1
	t1 := R
	fp[0] := t1
END FUNCTION main

