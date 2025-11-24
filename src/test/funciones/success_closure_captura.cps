// ✅ Captura de variable externa por función anidada (closure) y retorno correcto.
function mk(): integer {
  let base: integer = 10;          // variable externa
  function add(n: integer): integer {
    return base + n;               // ok: usa 'base' capturada
  }
  return add(5);                   // ok: integer
}

let r: integer = mk();             // ok
