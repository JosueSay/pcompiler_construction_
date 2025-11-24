function main(): void {
  let a: integer = 2;
  let b: integer = 3;
  let c: integer = 4;
  let z: integer = (a + b) * (c - b);
  let t: boolean = (z < 10) || (z > 20) && (a != b);
}
