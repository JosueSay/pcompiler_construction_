; Compiscript TAC
; program: 20251124-112617_negacion.cps
; generated: 2025-11-24T11:26:17

FUNCTION main:
	fp[0] := 1
	t0 := fp[0] == 1
	IF t0 > 0 GOTO IF_ELSE3
	GOTO IF_THEN1
IF_THEN1:
	fp[0] := 9
	GOTO IF_END2
IF_ELSE3:
	fp[0] := 7
IF_END2:
END FUNCTION main

