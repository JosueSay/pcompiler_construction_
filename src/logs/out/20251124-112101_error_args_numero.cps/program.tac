; Compiscript TAC
; program: 20251124-112101_error_args_numero.cps
; generated: 2025-11-24T11:21:01

FUNCTION f:
	t0 := fp[8] + fp[12]
	RETURN t0
END FUNCTION f

	PARAM 1
	CALL f, 1
	t1 := R
	gp[0] := t1
	PARAM 1
	PARAM 2
	PARAM 3
	CALL f, 3
	t1 := R
	gp[4] := t1
