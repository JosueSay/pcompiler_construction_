; Compiscript TAC
; program: 20251124-112605_for_azucar_while.cps
; generated: 2025-11-24T11:26:05

	gp[0] := 0
	gp[4] := 0
FOR_START1:
	t0 := gp[4] < 3
	IF t0 > 0 GOTO FOR_BODY2
	GOTO FOR_END3
FOR_BODY2:
	t1 := gp[0] + gp[4]
	gp[0] := t1
	GOTO FOR_START1
FOR_END3:
