; Compiscript TAC
; program: 20251124-112044_success_arit_log_comp.cps
; generated: 2025-11-24T11:20:44

	t0 := 2 * 3
	t0 := 1 + t0
	gp[0] := t0
	t0 := 10 - 4
	t1 := t0 / 2
	gp[4] := t1
	t1 := 7 % 3
	gp[8] := t1
	gp[12] := 10
	gp[16] := 20
	t2 := gp[12] < gp[16]
	gp[20] := t2
	t2 := gp[12] <= 20
	t3 := gp[16] >= 10
	t3 := t2 && t3
	gp[21] := t3
	t3 := gp[12] == 10
	gp[22] := t3
	gp[23] := true
	gp[24] := false
	t3 := ! gp[24]
	t3 := gp[23] && t3
	t2 := gp[12] < gp[16]
	t2 := t3 || t2
	gp[25] := t2
	t1 := "a" + "b"
	gp[26] := t1
