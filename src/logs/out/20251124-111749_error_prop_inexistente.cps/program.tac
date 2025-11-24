; Compiscript TAC
; program: 20251124-111749_error_prop_inexistente.cps
; generated: 2025-11-24T11:17:49

FUNCTION A_constructor:
	t0 := 0
	t1 := t0
	this[t1] := 1
END FUNCTION A_constructor

	t2 = newobj A, 4
	PARAM t2
	CALL A_constructor, 1
	gp[0] := t2
	gp[8] := gp[0]
