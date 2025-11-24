let op: integer = 1;
let r: integer = 0;
switch (op) {
  case 0:
    r = 10;
    break;
  case 1:
    r = 20;         // sin break → cae a default
  default:
    r = r + 1;
}
