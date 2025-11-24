; Compiscript TAC
; program: 20251124-112102_error_args_tipo.cps
; generated: 2025-11-24T11:21:02

FUNCTION g:
	t0 := fp[8] + fp[12]
	RETURN t0
END FUNCTION g

	PARAM "1"
	PARAM 2
	CALL g, 2
	t1 := R
	gp[0] := t1
	PARAM 1
	PARAM true
	CALL g, 2
	t1 := R
	gp[4] := t1
