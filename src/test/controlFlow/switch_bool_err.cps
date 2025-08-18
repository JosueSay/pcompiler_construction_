function f(): void {
  let b: boolean = true;
  switch (b) {
    case 0: { }     // ← incompatible (integer vs boolean)
  }
}
