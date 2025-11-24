; Compiscript TAC
; program: 20251124-112606_for_basic_d2.cps
; generated: 2025-11-24T11:26:06

FUNCTION main:
	fp[0] := 0
	fp[4] := 0
FOR_START1:
	t0 := fp[4] < 3
	IF t0 > 0 GOTO FOR_BODY2
	GOTO FOR_END3
FOR_BODY2:
	t1 := fp[0] + fp[4]
	fp[0] := t1
	GOTO FOR_START1
FOR_END3:
END FUNCTION main

