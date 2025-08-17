class A {
  function m() {
    let v: integer = this;  // seguirá fallando por tipo incompatible (A vs integer) -> esperado
  }
}

// 'this' fuera de método:
print(this);                // ERROR: 'this' solo dentro de métodos
