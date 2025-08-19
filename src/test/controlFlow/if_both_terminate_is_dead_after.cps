function f(): integer {
  if (true) {
    return 1;
  } else {
    return 2;
  }
  let z: integer = 0; // <- DEAD
}