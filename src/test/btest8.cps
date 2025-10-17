class A {
    let a: integer;
}

class B {
    let b: integer;
    let c: A;
}

function factorial(n: integer): integer{
  if (n==0){
    return 1;
  } else {
    return n * factorial(n-1);
  }
}

function main(): void {
    let y: B;
    y.b = 5;
    // y.c.a = factorial(y.b);
    y.c.a = 6;
}
