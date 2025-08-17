class Animal {
  // miembros opcionales por ahora
}

let a: Animal;                                // ok (tipado por clase conocida)
let xs: Animal[] = [ new Animal() ];          // ok (array de Animal)
let ys: Animal[][] = [ [ new Animal() ] ];    // ok (array 2D de Animal)
let zs: Animal[][] = [[ new Animal() ]];      // ok
let n: Animal = null;                         // ok (null asignable a referencia)
let arr: Animal[] = null;                     // ok (null asignable a referencia)
