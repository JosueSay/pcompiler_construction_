class D { 
  var data: integer[];
  function constructor(): void { this.data = [0]; }
}

function f(): void {
  return;
  this.data[0] = 1; // ERROR esperado: código inalcanzable / no emitir TAC
}
