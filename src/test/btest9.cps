// ------------------ Definición de structs como clases ------------------

class A {
    let a: integer;
}

class B {
    let b: integer[] = [0, 0, 0, 0, 0]; // tamaño 5 como en tu ejemplo
    let c: A = new A();               // inicialización para que c no sea null
}

// ------------------ Clase principal ------------------

class Program {

    // Variables globales de la clase
    let y: A = new A();
    let z: A = new A();

    // Funciones auxiliares
    function InputInt(): integer {
        return 0; // simulación de entrada
    }

    function OutputInt(n: integer): void {
        // simulación de salida
    }

    function ReturnNumber(): integer {
        return this.z.a;
    }

    // Factorial recursivo
    function factorial(n: integer): integer {
        if (n == 0) {
            return 1;
        } else {
            return n * this.factorial(n - 1);
        }
    }

    // Función principal
    function main(): void {
        let y: B[] = [new B(), new B(), new B(), new B(), new B()]; // array local de structs B
        let i: integer = 0;
        let j: integer = 0;
        let k: integer;

        this.z.a = 3;

        while (i <= 10) {
            y[j].b[0] = this.InputInt();

            if (y[j].b[0] == 5) {
                y[j].b[0] = this.z.a;
                k = this.factorial(this.ReturnNumber());
                this.OutputInt(k);
            }

            y[j].c.a = this.factorial(y[j].b[0]);
            this.OutputInt(y[j].c.a);

            i = i + 1;
        }
    }
}
