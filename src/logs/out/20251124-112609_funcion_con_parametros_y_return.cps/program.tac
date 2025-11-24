; Compiscript TAC
; program: 20251124-112609_funcion_con_parametros_y_return.cps
; generated: 2025-11-24T11:26:09

FUNCTION add:
	t0 := fp[8] + fp[12]
	RETURN t0
END FUNCTION add

	gp[0] := 4
	gp[4] := 7
	PARAM gp[0]
	PARAM gp[4]
	CALL add, 2
	t1 := R
	gp[8] := t1
