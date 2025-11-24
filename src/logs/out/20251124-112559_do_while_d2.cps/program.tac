; Compiscript TAC
; program: 20251124-112559_do_while_d2.cps
; generated: 2025-11-24T11:25:59

FUNCTION main:
	fp[0] := 2
DO_BODY1:
	t0 := fp[0] - 1
	fp[0] := t0
DO_COND2:
	t1 := fp[0] > 0
	IF t1 > 0 GOTO DO_BODY1
	GOTO DO_END3
DO_END3:
END FUNCTION main

