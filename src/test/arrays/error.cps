// Error: arreglo vacío
var vacio: integer[] = [];

// Error: tipos inconsistentes
var mixto: integer[] = [1, "texto", 3];

// Error: índice no entero
var nums: integer[] = [1, 2, 3];
var x: integer = nums["cero"];

// Error: asignación incompatible
var letras: string[] = ["a", "b"];
var n: integer = letras[0];
