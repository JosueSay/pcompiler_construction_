class Box {
  let v: integer;
  function constructor(v: integer) { this.v = v; }
  function inc(d: integer): integer { return this.v + d; }
}
function main(): void {
  let b: Box = new Box(10);
  let r: integer = b.inc(5);
}
