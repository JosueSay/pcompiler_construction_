class Pair {
  let a: integer; 
  let b: integer;
  function constructor(a: integer, b: integer) { this.a = a; this.b = b; }
  function sum(): integer { return this.a + this.b; }
}
function twice(x: integer): integer { return x + x; }

function main(): void {
  let p: Pair = new Pair(2, 5);
  let arr: integer[] = [10, 20, 30];
  let i: integer = 0;
  let acc: integer = 0;

  while (i < 3) {
    acc = acc + arr[i];
    i = i + 1;
  }

  if (acc > 30 && p.sum() > 0) {
    let t: integer = twice(p.sum());
    arr[1] = t;
  } else {
    arr[2] = 99;
  }
}
