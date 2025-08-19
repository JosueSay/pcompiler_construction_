function f(): void {
  break;        // error: fuera de bucle
  continue;     // error: fuera de bucle
  while (true) {
    break;      // ok
    continue;   // ok
  }
}
