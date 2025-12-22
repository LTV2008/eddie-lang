## Basics

### Printing to Console

```
// Using the println() function will print the text and create a line break 
println("Hello")
println("world.")
// Result:
// Hello
// world.

// Using the print() statement does NOT create a line break
print("Hello world. ")
print("How are you?")
// Result:
// Hello world. How are you?
```

### Variables

```
// Declare a variable
var myVarName;

// Initialize a variable
var myVarName = 5;

// Assign to an existing variable
myVarName = 10;

// Print a variable
println(myVarName)
println("The value is: " + myValue)

// Variables can also be declared and initialized using the keyword 'let'
let myVarName;
let myVarname = 5;

// If a variable isn't going to change its value, it is best to use the keyword 'const'
const PI = 3.141592653589793;
PI = 5;      // This will give an error
```

### User Input

```
// Read a string
var str = readLine(prompt)

// Read an integer
var num = readInt(prompt)

// Read a float
var cost = readFloat(prompt)

// Read a boolean
var bool = readBoolean(prompt)

// Example with specific prompts
var name = readLine("What is your name? ")
var age = readInt("What is your age? ")
var finishedWork = readBoolean("Is your work done? ")
```

### Math Operations

```
// Operators
+   Addition
-   Subtraction
*   Multiplication
/   Division
**  Exponentiation
%   Modulus (Remainder)
()  Parentheses (For order of operations)

// Examples
var z = x + y;
var w = x * y;

// Increment and Decrement
x++
x--

// Shorthand Operators
x += y;   // equivalent to x = x + y
x -= y;   // equivalent to x = x - y
x *= y;   // equivalent to x = x * y
x /= y;   // equivalent to x = x / y

// Exponentiation
var squared = 5 ** 2;  // prints 25

// Modulus
var z = 10 % 4;        // returns 2

// Mathematical Functions
var abs = Math.abs(x)
var sqrt = Math.sqrt(x)

// Rounding
var roundedPi = Math.round(3.14)    // returns 3
var floorResult = Math.floor(5/2)   // returns 2
```

### Random Numbers

```
// Generate random numbers
var roll = RandomizerInt(1, 6)
var color = RandomizerColor()

// Random generation functions
RandomizerInt(low, high)
RandomizerBoolean()
RandomizerFloat(low, high)
RandomizerColor()
```

### Strings

```
// String operations
var str = "hello";
var len = str.length;           // returns 5
var pos = str.indexOf("l");     // returns 2
var sub = str.substring(1, 4);  // returns "ell"

// String interpolation
println("Hello /(name)! /n How are you today?")
```

### Functions

```
// Basic function
function printText(input) {
    println(input)
}

// Function with return value
function addTwo(number) {
    return number + 2;
}
```

### Control Structures

```
// Waiting
wait(5)
sleep(5)

// Booleans
var myBoolean = true;
var x = !y;     // Not operator
var andExp = x && y;   // And operator
var orExp = x || y;    // Or operator

// If Statements
if (BOOLEAN_EXPRESSION) {
    // code to execute if true
}

if (BOOLEAN_EXPRESSION) {
    // code if true
} else {
    // code if false
}

// Loops
repeat(10) {
