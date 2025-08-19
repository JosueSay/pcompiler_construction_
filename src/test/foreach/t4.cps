function f(a: Foo[]): void {  // si Foo no está declarado, ya generas error
  foreach (x in a) { print(x); } // no debe explotar; solo propagar ErrorType
}
