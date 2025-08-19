function main(): void {
  let m: integer[][] = [[1,2],[3,4]];
  let ok: integer = m[1][1];  // OK (ambos literales dentro)
  let err: integer = m[2][0]; // ERROR: m tiene largo 2 ⇒ índices válidos 0..1
}
