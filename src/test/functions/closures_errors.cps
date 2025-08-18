function demo(x: integer): integer {
  if (true) {
    let y: integer = 1;

    function bad(): integer {
      return y + z;   // z no declarado (error)
    }
    return bad();
  }
  return x;
}
