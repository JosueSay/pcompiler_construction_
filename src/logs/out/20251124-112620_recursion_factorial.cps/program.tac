; Compiscript TAC
; program: 20251124-112620_recursion_factorial.cps
; generated: 2025-11-24T11:26:20

FUNCTION fact:
	t0 := fp[8] <= 1
	IF t0 > 0 GOTO IF_THEN1
	GOTO IF_END2
IF_THEN1:
	RETURN 1
IF_END2:
	t1 := fp[8] - 1
	PARAM t1
	CALL fact, 1
	t2 := R
	t1 := fp[8] * t2
	RETURN t1
END FUNCTION fact

	PARAM 4
	CALL fact, 1
	t2 := R
	gp[0] := t2
