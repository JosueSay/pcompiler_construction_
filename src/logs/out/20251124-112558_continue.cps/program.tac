; Compiscript TAC
; program: 20251124-112558_continue.cps
; generated: 2025-11-24T11:25:58

FUNCTION main:
	fp[0] := 0
	fp[4] := 0
WHILE_START1:
	t0 := fp[4] < 5
	IF t0 > 0 GOTO WHILE_BODY2
	GOTO WHILE_END3
WHILE_BODY2:
	t1 := fp[4] + 1
	fp[4] := t1
	t1 := fp[4] % 2
	t0 := t1 == 0
	IF t0 > 0 GOTO IF_THEN4
	GOTO IF_END5
IF_THEN4:
	GOTO WHILE_START1
IF_END5:
	t1 := fp[0] + fp[4]
	fp[0] := t1
	GOTO WHILE_START1
WHILE_END3:
END FUNCTION main

