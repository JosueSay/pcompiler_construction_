; Compiscript TAC
; program: 20251124-111754_success_herencia_override.cps
; generated: 2025-11-24T11:17:54

FUNCTION Animal_constructor:
	t0 := 0
	t1 := t0
	this[t1] := fp[16]
END FUNCTION Animal_constructor

FUNCTION Animal_hablar:
	t1 := 0
	t2 := t1
	t0 := this[t2]
	t3 := t0 + " hace ruido."
	RETURN t3
END FUNCTION Animal_hablar

FUNCTION Perro_hablar:
	t1 := 0
	t2 := t1
	t0 := this[t2]
	t3 := t0 + " ladra."
	RETURN t3
END FUNCTION Perro_hablar

	t0 = newobj Perro, 8
	PARAM t0
	PARAM "Toby"
	CALL Animal_constructor, 2
	gp[0] := t0
	PARAM gp[0]
	CALL Perro_hablar, 1
	t0 := R
	gp[8] := t0
