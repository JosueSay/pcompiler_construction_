; Compiscript TAC
; program: 20251124-112104_success_closure_captura.cps
; generated: 2025-11-24T11:21:04

FUNCTION mk:
	fp[0] := 10
FUNCTION add:
	t0 := fp[0] + fp[8]
	RETURN t0
END FUNCTION add

	t1 = mkenv base
	t2 = mkclos add, t1
	PARAM 5
	CALLC t2, 1
	t3 := R
	RETURN t3
END FUNCTION add

	CALL mk, 0
	t3 := R
	gp[0] := t3
