; Compiscript TAC
; program: 20251124-111709_error_index_no_entero.cps
; generated: 2025-11-24T11:17:09

	gp[0] := [10,20,30]
	t1 = len gp[0]
	IF "0"<0 GOTO oob1
	IF "0">=t1 GOTO oob1
	GOTO ok2
oob1:
	CALL __bounds_error, 0
ok2:
	t0 := gp[0]["0"]
	gp[8] := t0
	t1 = len gp[0]
	IF true<0 GOTO oob3
	IF true>=t1 GOTO oob3
	GOTO ok4
oob3:
	CALL __bounds_error, 0
ok4:
	t0 := gp[0][true]
	gp[12] := t0
