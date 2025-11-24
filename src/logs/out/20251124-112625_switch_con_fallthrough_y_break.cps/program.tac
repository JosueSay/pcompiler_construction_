; Compiscript TAC
; program: 20251124-112625_switch_con_fallthrough_y_break.cps
; generated: 2025-11-24T11:26:25

	gp[0] := 1
	gp[4] := 0
	IF gp[0] == 0 GOTO Lcase3
	IF gp[0] == 1 GOTO Lcase4
	GOTO Ldef2
Lcase3:
	gp[4] := 10
	GOTO Lend1
Lcase4:
	gp[4] := 20
Ldef2:
	t0 := gp[4] + 1
	gp[4] := t0
Lend1:
