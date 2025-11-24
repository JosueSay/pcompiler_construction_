; Compiscript TAC
; program: 20251124-112550_class_test_v10.cps
; generated: 2025-11-24T11:25:50

FUNCTION Box_constructor:
	t0 := 0
	t1 := t0
	this[t1] := [7,8,9]
END FUNCTION Box_constructor

FUNCTION Box_get:
	t1 := 0
	t2 := t1
	t0 := this[t2]
	t1 = len t0
	IF fp[16]<0 GOTO oob1
	IF fp[16]>=t1 GOTO oob1
	GOTO ok2
oob1:
	CALL __bounds_error, 0
ok2:
	t2 := t0[fp[16]]
	RETURN t2
END FUNCTION Box_get

FUNCTION main:
	t0 = newobj Box, 8
	PARAM t0
	CALL Box_constructor, 1
	fp[0] := t0
	PARAM fp[0]
	PARAM 1
	CALL Box_get, 2
	t1 := R
	fp[8] := t1
END FUNCTION main

