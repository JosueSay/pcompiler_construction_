; Compiscript TAC
; program: 20251124-112042_error_op_logico_no_boolean.cps
; generated: 2025-11-24T11:20:42

	gp[0] := 1
	gp[4] := "s"
	t0 := gp[0] && true
	gp[12] := t0
	t0 := gp[4] || false
	gp[13] := t0
	t0 := ! gp[0]
	gp[14] := t0
