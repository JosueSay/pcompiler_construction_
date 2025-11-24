; Compiscript TAC
; program: 20251124-112608_func_params_return_d2.cps
; generated: 2025-11-24T11:26:08

FUNCTION add:
	t0 := fp[8] + fp[12]
	RETURN t0
END FUNCTION add

FUNCTION main:
	fp[0] := 4
	fp[4] := 7
	t0 := fp[0] + 1
	PARAM t0
	PARAM fp[4]
	CALL add, 2
	t1 := R
	fp[8] := t1
END FUNCTION main

