; Compiscript TAC
; program: 20251124-112105_success_params_y_return.cps
; generated: 2025-11-24T11:21:05

FUNCTION suma:
	t0 := fp[8] + fp[12]
	RETURN t0
END FUNCTION suma

	PARAM 2
	PARAM 3
	CALL suma, 2
	t1 := R
	gp[0] := t1
