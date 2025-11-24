; Compiscript TAC
; program: 20251124-111752_success_constructor_args.cps
; generated: 2025-11-24T11:17:52

FUNCTION A_constructor:
	t0 := fp[16] + fp[20]
	t1 := 0
	t2 := t1
	this[t2] := t0
END FUNCTION A_constructor

	t3 = newobj A, 4
	PARAM t3
	PARAM 1
	PARAM 2
	CALL A_constructor, 3
	gp[0] := t3
