function f(): void {
  let x: integer = 1;
  switch (x) {
    case 1: { }          // ok
    case "hola": { }     // error: tipo incompatible con integer
    default: { }
  }
}
