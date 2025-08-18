class Person {
    var name: string;
    var age: integer;

    function greet(): void {
        print("Hello, I am " + this.name);
    }
}

class Student : Person {
    var major: string;

    function greet(): void {
        print("I am " + this.name + " and I study " + this.major);
    }
}

struct Point {
    var x: integer;
    var y: integer;
}

function main(): void {
    var p = new Person();
    p.name = "Alice";
    p.age = 30;
    p.greet();

    var s = new Student();
    s.name = "Bob";
    s.major = "CS";
    s.greet();

    var pt = Point();
    pt.x = 10;
    pt.y = 20;
    print("Point: " + pt.x + ", " + pt.y);
}
