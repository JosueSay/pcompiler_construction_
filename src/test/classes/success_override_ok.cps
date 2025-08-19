class Calculadora {
  function suma(a: integer, b: integer): integer {
    return a + b;
  }
}

class CalcAvanzada : Calculadora {
  // Override válido: misma firma (a: integer, b: integer) -> integer
  function suma(a: integer, b: integer): integer {
    // (podría hacer otra cosa, pero la firma coincide)
    return (a + b) + 1; 
  }
}

function main(): void {
  let c: CalcAvanzada = new CalcAvanzada();
  let r: integer = c.suma(2, 3); // OK
}
