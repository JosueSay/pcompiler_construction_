// Caso A: cambia parámetros
class Figura {
  function area(): integer { return 0; }
}

class Circulo : Figura {
  // ERROR: firma distinta (agrega parámetro)
  function area(radio: integer): integer {
    return radio * radio;
  }
}

// Caso B: cambia tipo de retorno
class Animal {
  function hablar(): string { return "???"; }
}

class Perro : Animal {
  // ERROR: firma distinta (retorno integer en vez de string)
  function hablar(): integer { 
    return 1; 
  }
}
