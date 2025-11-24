; Compiscript TAC
; program: 20251124-112156_error_codigo_muerto_return.cps
; generated: 2025-11-24T11:21:56

FUNCTION f:
	RETURN 1
END FUNCTION f

FUNCTION main:
	CALL f, 0
	t0 := R
END FUNCTION main

