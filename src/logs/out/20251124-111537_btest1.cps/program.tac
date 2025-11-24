; Compiscript TAC
; program: 20251124-111537_btest1.cps
; generated: 2025-11-24T11:15:37

FUNCTION m:
	RETURN 0
END FUNCTION m

FUNCTION main:
	fp[8] := 0
WHILE_START1:
	t0 := fp[8] <= 20
	IF t0 > 0 GOTO WHILE_BODY2
	GOTO WHILE_END3
WHILE_BODY2:
	t1 := fp[8] + 1
	fp[8] := t1
	PARAM fp[8]
	CALL m, 1
	t2 := R
	GOTO WHILE_START1
WHILE_END3:
END FUNCTION main

