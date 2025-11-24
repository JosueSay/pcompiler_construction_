class C {
  let x: integer;
  function constructor(v: integer) { this.x = v; }
}
function main(): void {
  let o: C = new C(10);
  let y: integer = o.x;
  o.x = y + 2;
}
