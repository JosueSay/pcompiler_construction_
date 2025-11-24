; Compiscript TAC
; program: 20251123-194739_program.cps
; generated: 2025-11-23T19:47:40

FUNCTION toString:
	RETURN ""
END FUNCTION toString

FUNCTION Persona_constructor:
	t0 := 0
	t1 := t0
	this[t1] := fp[16]
	t1 := 8
	t0 := t1
	this[t0] := fp[24]
	t0 := 12
	t1 := t0
	this[t1] := "rojo"
END FUNCTION Persona_constructor

FUNCTION Persona_saludar:
	t1 := 0
	t2 := t1
	t0 := this[t2]
	t3 := "Hola, mi nombre es " + t0
	RETURN t3
END FUNCTION Persona_saludar

FUNCTION Persona_incrementarEdad:
	t1 := 8
	t2 := t1
	t0 := this[t2]
	t3 := t0 + fp[16]
	t2 := 8
	t1 := t2
	this[t1] := t3
	t1 := 8
	t2 := t1
	t0 := this[t2]
	PARAM t0
	CALL toString, 1
	t4 := R
	t3 := "Ahora tengo " + t4
	t5 := t3 + " años."
	RETURN t5
END FUNCTION Persona_incrementarEdad

FUNCTION Estudiante_constructor:
	t0 := 0
	t1 := t0
	this[t1] := fp[16]
	t1 := 8
	t0 := t1
	this[t0] := fp[24]
	t0 := 12
	t1 := t0
	this[t1] := "rojo"
	t1 := 20
	t0 := t1
	this[t0] := fp[28]
END FUNCTION Estudiante_constructor

FUNCTION Estudiante_estudiar:
	t1 := 0
	t2 := t1
	t0 := this[t2]
	t3 := t0 + " está estudiando en "
	t1 := 20
	t4 := t1
	t2 := this[t4]
	PARAM t2
	CALL toString, 1
	t5 := R
	t6 := t3 + t5
	t7 := t6 + " grado."
	RETURN t7
END FUNCTION Estudiante_estudiar

FUNCTION Estudiante_promedioNotas:
	t0 := fp[16] + fp[20]
	t1 := t0 + fp[24]
	t2 := t1 / 3
	fp[0] := t2
	RETURN fp[0]
END FUNCTION Estudiante_promedioNotas

	gp[0] := ""
	gp[8] := "Erick"
	t3 = newobj Estudiante, 24
	PARAM t3
	PARAM gp[8]
	PARAM 20
	PARAM 3
	CALL Estudiante_constructor, 4
	gp[16] := t3
	PARAM gp[16]
	CALL Persona_saludar, 1
	t3 := R
	t0 := gp[0] + t3
	t2 := t0 + "\n"
	gp[0] := t2
	PARAM gp[16]
	CALL Estudiante_estudiar, 1
	t3 := R
	t0 := gp[0] + t3
	t2 := t0 + "\n"
	gp[0] := t2
	PARAM gp[16]
	PARAM 5
	CALL Persona_incrementarEdad, 2
	t3 := R
	t0 := gp[0] + t3
	t2 := t0 + "\n"
	gp[0] := t2
	gp[24] := 1
WHILE_START1:
	t4 := gp[24] <= 5
	IF t4 > 0 GOTO WHILE_BODY2
	GOTO WHILE_END3
WHILE_BODY2:
	t0 := gp[24] % 2
	t4 := t0 == 0
	IF t4 > 0 GOTO IF_THEN4
	GOTO IF_ELSE6
IF_THEN4:
	PARAM gp[24]
	CALL toString, 1
	t3 := R
	t0 := gp[0] + t3
	t2 := t0 + " es par\n"
	gp[0] := t2
	GOTO IF_END5
IF_ELSE6:
	PARAM gp[24]
	CALL toString, 1
	t3 := R
	t0 := gp[0] + t3
	t2 := t0 + " es impar\n"
	gp[0] := t2
IF_END5:
	t0 := gp[24] + 1
	gp[24] := t0
	GOTO WHILE_START1
WHILE_END3:
	t6 := gp[16]
	t7 := 8
	t8 := t7
	t5 := t6[t8]
	t0 := t5 * 2
	t2 := 5 - 3
	t1 := t2 / 2
	t1 := t0 + t1
	gp[28] := t1
	t1 := gp[0] + "Resultado de la expresión: "
	PARAM gp[28]
	CALL toString, 1
	t3 := R
	t0 := t1 + t3
	t2 := t0 + "\n"
	gp[0] := t2
	gp[32] := 0
	PARAM gp[16]
	PARAM 90
	PARAM 85
	PARAM 95
	CALL Estudiante_promedioNotas, 4
	t5 := R
	gp[32] := t5
	t0 := gp[0] + "Promedio (entero): "
	PARAM gp[32]
	CALL toString, 1
	t3 := R
	t1 := t0 + t3
	t2 := t1 + "\n"
	gp[0] := t2
