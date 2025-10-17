function gcd(v: integer, u: integer): integer{
  if (v==0){
    return u;
  }
  else {
    return gcd(v,u-(u/v)*v);
  }
}

function main(): void {
  let x: integer;
  let y: integer;
  let z: integer;
  
  x = 10;
  y=5;
  z=gcd(x,y);
}

