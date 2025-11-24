; Compiscript TAC
; program: 20251124-111847_success_for_continue.cps
; generated: 2025-11-24T11:18:47

	gp[0] := 0
	gp[0] := 0
FOR_START1:
	t0 := gp[0] < 3
	IF t0 > 0 GOTO FOR_BODY2
	GOTO FOR_END3
FOR_BODY2:
	t0 := gp[0] == 1
	IF t0 > 0 GOTO IF_THEN5
	GOTO IF_END6
IF_THEN5:
	GOTO FOR_STEP4
IF_END6:
	t1 := gp[0] + 2
	gp[0] := t1
FOR_STEP4:
	GOTO FOR_START1
FOR_END3:
