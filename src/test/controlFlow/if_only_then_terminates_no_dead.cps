function f(): integer {
  if (true) {
    return 1;
  }
  let z: integer = 0; // <- OK (no DEAD)
  return 2;
}