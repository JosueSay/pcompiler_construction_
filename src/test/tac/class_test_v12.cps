class Box {
  var data: integer[];
  function constructor(){ this.data = [0,0,0,0]; }
  function put(i: integer, v: integer): void {
    this.data[i] = v; // Debe emitir FIELD_LOAD -> t_arr, INDEX_STORE t_arr[i]=v, y liberar t_arr (o al final por reset)
  }
}

function main(): void {
  let b: Box = new Box();
  b.put(2, 99);
}
