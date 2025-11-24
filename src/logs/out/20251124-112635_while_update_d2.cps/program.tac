; Compiscript TAC
; program: 20251124-112635_while_update_d2.cps
; generated: 2025-11-24T11:26:35

FUNCTION main:
	fp[0] := 0
	fp[4] := 3
	fp[8] := 0
WHILE_START1:
	t0 := fp[0] < fp[4]
	IF t0 > 0 GOTO WHILE_BODY2
	GOTO WHILE_END3
WHILE_BODY2:
	t1 := fp[8] + fp[0]
	fp[8] := t1
	t1 := fp[0] + 1
	fp[0] := t1
	GOTO WHILE_START1
WHILE_END3:
END FUNCTION main

