// ✅ Override válido: misma firma y retorno.
class Animal {
  let nombre: string;
  function constructor(nombre: string) { this.nombre = nombre; }
  function hablar(): string { return this.nombre + " hace ruido."; }
}
class Perro : Animal {
  function hablar(): string { return this.nombre + " ladra."; } // ok: firma coincide
}
let p: Perro = new Perro("Toby");
let s: string = p.hablar();  // ok
