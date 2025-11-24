; Compiscript TAC
; program: 20251124-111545_btest7.cps
; generated: 2025-11-24T11:15:45

FUNCTION gcd:
	t0 := fp[8] == 0
	IF t0 > 0 GOTO IF_THEN1
	GOTO IF_ELSE3
IF_THEN1:
	RETURN fp[12]
IF_ELSE3:
	t1 := fp[12] / fp[8]
	t2 := t1 * fp[8]
	t2 := fp[12] - t2
	PARAM fp[8]
	PARAM t2
	CALL gcd, 2
	t3 := R
	RETURN t3
END FUNCTION gcd

FUNCTION main:
	fp[0] := 10
	fp[4] := 5
	PARAM fp[0]
	PARAM fp[4]
	CALL gcd, 2
	t0 := R
	fp[8] := t0
END FUNCTION main

