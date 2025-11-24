; Compiscript TAC
; program: 20251124-111711_success_index_entero.cps
; generated: 2025-11-24T11:17:11

	gp[0] := [10,20,30]
	gp[8] := 1
	t1 = len gp[0]
	IF gp[8]<0 GOTO oob1
	IF gp[8]>=t1 GOTO oob1
	GOTO ok2
oob1:
	CALL __bounds_error, 0
ok2:
	t0 := gp[0][gp[8]]
	gp[12] := t0
	t2 := 2
	t1 = len gp[0]
	IF t2<0 GOTO oob3
	IF t2>=t1 GOTO oob3
	GOTO ok4
oob3:
	CALL __bounds_error, 0
ok4:
	t0 := gp[0][t2]
	gp[16] := t0
