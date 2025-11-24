; Compiscript TAC
; program: 20251124-112610_if_else_corto_circuito.cps
; generated: 2025-11-24T11:26:10

	gp[0] := 5
	gp[4] := 10
	t0 := gp[0] < 3
	IF t0 > 0 GOTO IF_THEN1
	GOTO Lor4
Lor4:
	t0 := gp[4] > 7
	IF t0 > 0 GOTO Land5
	GOTO IF_ELSE3
Land5:
	t0 := gp[0] != gp[4]
	IF t0 > 0 GOTO IF_THEN1
	GOTO IF_ELSE3
IF_THEN1:
	gp[0] := 0
	GOTO IF_END2
IF_ELSE3:
	gp[0] := 1
IF_END2:
