let z: integer;

function factorial(n: integer): integer{
  if (n==0){
    return 1;
  }
  else {
    return n*factorial(n-1);
  }
}

function main(): void {
  let y: integer;
  z = y*2;
  y = factorial(z);
}

