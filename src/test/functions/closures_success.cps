function outer(a: integer): integer {
  let k: integer = 2;

  function inner(b: integer): integer {
    // captura a y k
    return a + b + k;
  }

  return inner(5);
}

let r: integer = outer(3);  // 3 + 5 + 2 = 10
