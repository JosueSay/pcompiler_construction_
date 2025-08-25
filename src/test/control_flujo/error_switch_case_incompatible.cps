// ❌ Tipos incompatibles entre switch y case.
let x: integer = 1;
switch (x) {
  case "uno": { } // error semántico: case string vs switch integer
  default: { }
}