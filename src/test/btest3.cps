function OutputInt(n: integer): void {
}

function InputInt(): integer {
  return 0;
}

function fibonacci(n: integer): integer {
  let r: integer;
  if (n == 0) {
    r = 1;
  } else {
    if (n == 1) {
      r = 1;
    } else {
      r = fibonacci(n - 1) + fibonacci(n - 2);
    }
  }
  return r;
}

function main(): void {
  let n: integer;
  let f: integer;
  let i: integer;

  i = 0;
  while (i <= 20) {
    f = fibonacci(i);
    OutputInt(f);
    i = i + 1;
  }
}

