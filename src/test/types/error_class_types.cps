let p: Persona;                 // ERROR: Tipo de clase no declarado: 'Persona'
let lista: Persona[];           // ERROR igual
let matriz: Persona[][] = [];   // ERROR tipo no declarado + arreglo vacío no soportado
class Animal { }
let x: Animal[] = [ 1 ];        // ERROR: integer[] vs Animal[]
let ys: Animal[][] = [[1]];     // ERROR: integer[][] vs Animal[][]
