function sum(a: integer, b: integer): integer {
  let tmp: integer = a + b;
  {
    let tmp: integer = 1; // sombra permitido en bloque interno
  }
  print(tmp);
  return a + b; // (validación de return llegará después)
}

let x: integer = 3;
let y: integer = 4;
// 'a' y 'b' no son visibles aquí (son params de la función)
