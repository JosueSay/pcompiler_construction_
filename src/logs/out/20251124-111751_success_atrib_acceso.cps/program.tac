; Compiscript TAC
; program: 20251124-111751_success_atrib_acceso.cps
; generated: 2025-11-24T11:17:51

FUNCTION A_constructor:
	t0 := 0
	t1 := t0
	this[t1] := fp[16]
END FUNCTION A_constructor

	t2 = newobj A, 4
	PARAM t2
	PARAM 5
	CALL A_constructor, 2
	gp[0] := t2
	t3 := gp[0]
	t0 := 0
	t4 := t0
	t1 := t3[t4]
	gp[8] := t1
