// for con continue (verifica que continue salte a step)
let i: integer = 0;
for (i = 0; i < 3; i = i + 1) {
  if (i == 1) { continue; }
  i = i + 2;
}
