class A {
  const C: integer = 1;
  let x: integer = 0;              // inicializada (no-ref)
  function m(y: integer): integer {
    let z: integer = this.C + y;   // ahora property access funciona (MVP)
    return z;
  }
}

function g(p: integer): integer {
  let q: integer = p;
  return q;
}
