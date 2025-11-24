; Compiscript TAC
; program: 20251124-112607_for_sin_condicion_explicita.cps
; generated: 2025-11-24T11:26:07

	gp[0] := 0
	gp[4] := 0
FOR_START1:
	GOTO FOR_BODY2
FOR_BODY2:
	t0 := gp[4] == 3
	IF t0 > 0 GOTO IF_THEN5
	GOTO IF_END6
IF_THEN5:
	GOTO FOR_END3
IF_END6:
	t1 := gp[0] + gp[4]
	gp[0] := t1
	GOTO FOR_START1
FOR_END3:
