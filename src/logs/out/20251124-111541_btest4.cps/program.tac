; Compiscript TAC
; program: 20251124-111541_btest4.cps
; generated: 2025-11-24T11:15:41

FUNCTION suma:
	t0 := fp[8] + fp[12]
	RETURN t0
END FUNCTION suma

FUNCTION main:
	t0 := fp[0] * fp[4]
	t0 := gp[0] + t0
	gp[0] := t0
END FUNCTION main

