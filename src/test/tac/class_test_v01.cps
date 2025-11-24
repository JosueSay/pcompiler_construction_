class Box {
  var data: integer[];
  function constructor(n: integer): void {
    this.data = [0,0,0,0];
  }
  function put(i: integer, v: integer): void {
    this.data[i] = v;
  }
  function get(i: integer): integer {
    return this.data[i];
  }
}

let b: Box = new Box(4);
b.put(2, 99);
let q: integer = b.get(2);
