; Compiscript TAC
; program: 20251124-111548_debug_program.cps
; generated: 2025-11-24T11:15:48

	gp[0] := 1
	gp[4] := "hola"
	gp[12] := true
	t0 := "Hola " + "mundo"
	gp[13] := t0
	gp[21] := 5
	t0 := 1 + true
	gp[25] := t0
	t0 := 1 + 2
	gp[29] := t0
	t1 := 1 < 2
	t2 := t1 && true
	gp[33] := t2
	gp[34] := [1,2,3]
	t0 := 1
	t4 = len gp[34]
	IF t0<0 GOTO oob1
	IF t0>=t4 GOTO oob1
	GOTO ok2
oob1:
	CALL __bounds_error, 0
ok2:
	t3 := gp[34][t0]
	gp[42] := t3
FUNCTION suma:
	t0 := fp[8] + fp[12]
	RETURN t0
END FUNCTION suma

	PARAM 2
	PARAM 3
	CALL suma, 2
	t1 := R
	gp[46] := t1
FUNCTION toStringInt:
	RETURN "num"
END FUNCTION toStringInt

FUNCTION h:
	RETURN 1
END FUNCTION h

FUNCTION mk:
	fp[0] := 10
FUNCTION add:
	t0 := fp[0] + fp[8]
	RETURN t0
END FUNCTION add

	t1 = mkenv base
	t2 = mkclos add, t1
	PARAM 5
	CALLC t2, 1
	t3 := R
	RETURN t3
END FUNCTION add

	CALL mk, 0
	t3 := R
	gp[50] := t3
	gp[54] := 1
	t4 := gp[54] < 10
	IF t4 > 0 GOTO IF_THEN3
	GOTO IF_ELSE5
IF_THEN3:
	GOTO IF_END4
IF_ELSE5:
IF_END4:
	gp[58] := 0
WHILE_START6:
	t4 := gp[58] < 3
	IF t4 > 0 GOTO WHILE_BODY7
	GOTO WHILE_END8
WHILE_BODY7:
	t0 := gp[58] + 1
	gp[58] := t0
	GOTO WHILE_START6
WHILE_END8:
	gp[62] := 2
	IF gp[62] == 1 GOTO Lcase11
	IF gp[62] == 2 GOTO Lcase12
	GOTO Ldef10
Lcase11:
Lcase12:
Ldef10:
Lend9:
FUNCTION A_constructor:
	t0 := 0
	t1 := t0
	this[t1] := fp[16]
END FUNCTION A_constructor

FUNCTION A_saludar:
	RETURN "A"
END FUNCTION A_saludar

FUNCTION B_constructor:
	t0 := 0
	t1 := t0
	this[t1] := fp[16]
END FUNCTION B_constructor

FUNCTION B_saludar:
	RETURN "B"
END FUNCTION B_saludar

FUNCTION B_doble:
	t1 := 0
	t2 := t1
	t0 := this[t2]
	t1 := 0
	t3 := t1
	t2 := this[t3]
	t4 := t0 + t2
	RETURN t4
END FUNCTION B_doble

	t5 = newobj A, 4
	PARAM t5
	PARAM 5
	CALL A_constructor, 2
	gp[66] := t5
	t5 = newobj B, 4
	PARAM t5
	PARAM 7
	CALL B_constructor, 2
	gp[74] := t5
	t6 := gp[74]
	t2 := 0
	t3 := t2
	t0 := t6[t3]
	gp[82] := t0
	PARAM gp[74]
	CALL B_saludar, 1
	t5 := R
	gp[86] := t5
FUNCTION foo:
END FUNCTION foo

	gp[94] := ""
	PARAM gp[82]
	CALL toStringInt, 1
	t0 := R
	t1 := gp[94] + t0
	t2 := t1 + gp[86]
	gp[94] := t2
