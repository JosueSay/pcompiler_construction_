// Clase simple con atributo y método
class Persona {
  let nombre: string;

  function constructor(nombre: string) {
    this.nombre = nombre;
  }

  function saludar(): string {
    return "Hola " + this.nombre;
  }
}

function main(): void {
  let p: Persona = new Persona("Ana");
  let x: string = p.nombre;   // acceso a propiedad
  p.nombre = "Maria";         // asignación válida
  let saludo: string = p.saludar(); // método ok
}

// Herencia simple
class Animal {
  let nombre: string;
  function constructor(nombre: string) {
    this.nombre = nombre;
  }
  function hablar(): string {
    return this.nombre + " hace ruido";
  }
}

class Perro : Animal {
  function constructor(nombre: string) {
    this.nombre = nombre;
  }
  function hablar(): string {
    return this.nombre + " ladra";
  }
}

function pruebaHerencia(): void {
  let dog: Perro = new Perro("Firulais");
  let sonido: string = dog.hablar(); // override válido
}
