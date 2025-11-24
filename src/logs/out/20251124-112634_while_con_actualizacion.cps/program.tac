; Compiscript TAC
; program: 20251124-112634_while_con_actualizacion.cps
; generated: 2025-11-24T11:26:34

	gp[0] := 0
	gp[4] := 3
WHILE_START1:
	t0 := gp[0] < gp[4]
	IF t0 > 0 GOTO WHILE_BODY2
	GOTO WHILE_END3
WHILE_BODY2:
	t1 := gp[0] + 1
	gp[0] := t1
	GOTO WHILE_START1
WHILE_END3:
