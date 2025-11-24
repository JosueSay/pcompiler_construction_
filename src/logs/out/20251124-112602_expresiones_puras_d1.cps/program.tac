; Compiscript TAC
; program: 20251124-112602_expresiones_puras_d1.cps
; generated: 2025-11-24T11:26:02

FUNCTION main:
	fp[0] := 2
	fp[4] := 3
	fp[8] := 4
	t0 := fp[0] + fp[4]
	t1 := fp[8] - fp[4]
	t1 := t0 * t1
	fp[12] := t1
	t2 := fp[12] < 10
	t3 := fp[12] > 20
	t4 := fp[0] != fp[4]
	t4 := t3 && t4
	t4 := t2 || t4
	fp[16] := t4
END FUNCTION main

