class Counter {
  var x: integer;
  function constructor(init: integer): void { this.x = init; }
  function inc(): void { this.x = this.x + 1; }
  function get(): integer { return this.x; }
}

let c: Counter = new Counter(5);
c.inc();
let g: integer = c.get();
