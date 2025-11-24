; Compiscript TAC
; program: 20251124-111852_success_while_boolean.cps
; generated: 2025-11-24T11:18:52

	gp[0] := 0
WHILE_START1:
	t0 := gp[0] < 3
	IF t0 > 0 GOTO WHILE_BODY2
	GOTO WHILE_END3
WHILE_BODY2:
	t1 := gp[0] + 1
	gp[0] := t1
	GOTO WHILE_START1
WHILE_END3:
