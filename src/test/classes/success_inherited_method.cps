// Base con método; derivada NO overridea, debe encontrarse en la base
class Base {
  let nombre: string;

  function constructor(nombre: string) {
    this.nombre = nombre;
  }

  function saludo(): string {
    return "Hola " + this.nombre;
  }
}

class Derivada : Base {
  // sin métodos: usa los de Base
}

function main(): void {
  let d: Derivada = new Derivada("Ana");
  let s: string = d.saludo(); // OK: método definido en Base
}
