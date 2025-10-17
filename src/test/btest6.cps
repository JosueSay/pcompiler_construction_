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
  let i: integer;
  i = 0;
  while (i<10){
    if (i!=5){
      y = factorial(i);
    }
    i = i + 1;
  }
}

