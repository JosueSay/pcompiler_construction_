// 1) Asignación a propiedad inexistente
class Persona {
  let nombre: string;
}

function err1(): void {
  let p: Persona = new Persona();
  p.apellido = "Lopez"; // ERROR: atributo no existe
}

// 2) Tipo incorrecto en asignación de propiedad
class Libro {
  let paginas: integer;
}

function err2(): void {
  let l: Libro = new Libro();
  l.paginas = "cien"; // ERROR: string no asignable a integer
}

// 3) Constructor con firma incorrecta
class Animal {
  let nombre: string;
  function constructor(nombre: string) {
    this.nombre = nombre;
  }
}

function err3(): void {
  let a: Animal = new Animal(); // ERROR: faltan argumentos
}

// 4) Clase base inexistente
class Fantasma : NoExiste {
  let x: integer;
}

// 5) Override inválido (firma distinta)
class Figura {
  function area(): integer { return 0; }
}

class Circulo : Figura {
  function area(radio: integer): integer { // ERROR: firma distinta
    return radio * radio;
  }
}
