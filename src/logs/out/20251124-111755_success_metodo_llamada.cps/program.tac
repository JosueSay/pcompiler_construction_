; Compiscript TAC
; program: 20251124-111755_success_metodo_llamada.cps
; generated: 2025-11-24T11:17:55

FUNCTION Mathy_suma:
	t0 := fp[16] + fp[20]
	RETURN t0
END FUNCTION Mathy_suma

	t1 = newobj Mathy, 0
	gp[0] := t1
	PARAM gp[0]
	PARAM 2
	PARAM 3
	CALL Mathy_suma, 3
	t2 := R
	gp[8] := t2
