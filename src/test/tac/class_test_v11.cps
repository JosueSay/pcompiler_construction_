class AttrDup {
  var a: integer;
  var b: integer[];
  const K: integer = 1;

  function constructor(): void {
    this.a = 0;
    this.b = [0,0];
  }
}

function main(): void {
  let x: AttrDup = new AttrDup();
  x.b[1] = 5;
}
