class C {
  var x: integer;
  function constructor(): void { this.x = 0; }
}

function main(): void {
  let c: C = new C();
  c.x[0] = 1; // ERROR esperado: asig. indexada sobre no-arreglo
}
