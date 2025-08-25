// ❌ Código muerto: cualquier sentencia después de 'return' es inalcanzable.
function f(): integer {
  return 1;                // aquí termina el flujo de la función
  let x: integer = 2;      // error: código muerto (nunca se ejecuta)
}

function main(): void {
  f();
}
