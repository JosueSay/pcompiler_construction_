// ❌ 'this' solo es válido dentro de métodos/constructor.
function f(): integer {
  this.nombre = "X"; // error: 'this' fuera del contexto de un método/constructor de clase
  return 0;
}
