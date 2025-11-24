; Compiscript TAC
; program: 20251124-112618_obb_ge_len.cps
; generated: 2025-11-24T11:26:18

FUNCTION main:
	fp[0] := [1,2,3]
	fp[8] := 3
	t1 = len fp[0]
	IF fp[8]<0 GOTO oob1
	IF fp[8]>=t1 GOTO oob1
	GOTO ok2
oob1:
	CALL __bounds_error, 0
ok2:
	t0 := fp[0][fp[8]]
	fp[12] := t0
END FUNCTION main

