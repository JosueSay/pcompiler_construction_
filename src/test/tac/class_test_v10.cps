class Box {
  var data: integer[];
  function constructor(): void { this.data = [7,8,9]; }
  function get(i: integer): integer { return this.data[i]; }
}

function main(): void {
  let b: Box = new Box();
  let z: integer = b.get(1); // Debe generar FIELD_LOAD de this.data y luego INDEX_LOAD en tu backend (al menos FIELD_LOAD con _field_owner/_field_offset)
}
