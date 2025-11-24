; Compiscript TAC
; program: 20251124-112610_herencia_override_d2.cps
; generated: 2025-11-24T11:26:10

FUNCTION A_constructor:
	t0 := 0
	t1 := t0
	this[t1] := fp[16]
END FUNCTION A_constructor

FUNCTION A_get:
	t1 := 0
	t2 := t1
	t0 := this[t2]
	RETURN t0
END FUNCTION A_get

FUNCTION B_get:
	t1 := 0
	t2 := t1
	t0 := this[t2]
	t3 := t0 + 1
	RETURN t3
END FUNCTION B_get

FUNCTION main:
	t0 = newobj A, 4
	PARAM t0
	PARAM 3
	CALL A_constructor, 2
	fp[0] := t0
	t0 = newobj B, 4
	PARAM t0
	PARAM 4
	CALL A_constructor, 2
	fp[8] := t0
	PARAM fp[0]
	CALL A_get, 1
	t1 := R
	fp[16] := t1
	PARAM fp[8]
	CALL B_get, 1
	t1 := R
	fp[20] := t1
END FUNCTION main

