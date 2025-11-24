; Compiscript TAC
; program: 20251124-112611_if_else_shortcircuit_d2.cps
; generated: 2025-11-24T11:26:11

FUNCTION main:
	fp[0] := 15
	fp[4] := 5
	t0 := fp[0] < 10
	IF t0 > 0 GOTO IF_THEN1
	GOTO Lor4
Lor4:
	t0 := fp[0] > 20
	IF t0 > 0 GOTO Land5
	GOTO IF_ELSE3
Land5:
	t0 := fp[0] != fp[4]
	IF t0 > 0 GOTO IF_THEN1
	GOTO IF_ELSE3
IF_THEN1:
	fp[4] := 0
	GOTO IF_END2
IF_ELSE3:
	fp[4] := 1
IF_END2:
END FUNCTION main

