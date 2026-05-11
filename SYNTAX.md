# Eddie Language Syntax Documentation

Welcome to the **Eddie Language** - a simple DIY programming language written in Python. This document describes all acceptable syntax and features of the Eddie language interpreter.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Syntax](#basic-syntax)
3. [Data Types](#data-types)
4. [Variables](#variables)
5. [Operators](#operators)
6. [Control Flow](#control-flow)
7. [Built-in Functions](#built-in-functions)
8. [Comments](#comments)
9. [Examples](#examples)

---

## Getting Started

### Running Eddie Programs

**File Mode:**
```bash
python3 eddie-interpreter.py program.txt
```

**Interactive Mode (REPL):**
```bash
python3 eddie-interpreter.py
```

---

## Basic Syntax

Eddie uses a syntax similar to C-like languages with the following conventions:

- **Statements end with semicolons** (`;`)
- **Code blocks are enclosed in braces** (`{ }`)
- **Parentheses** (`()`) are used for conditions and function calls
- **Comments** use double slashes (`//`)
- **Identifiers** must start with a letter or underscore, followed by letters, digits, or underscores

---

## Data Types

Eddie supports the following data types:

| Type | Example | Description |
|------|---------|-------------|
| **Integer** | `42`, `-5`, `0` | Whole numbers |
| **Float** | `3.14`, `-2.5`, `0.0` | Decimal numbers |
| **String** | `"hello"`, `'world'` | Text enclosed in quotes |
| **Boolean** | `true`, `false` | Logical values |

### String Literals

Strings can be enclosed in either double or single quotes:
```
"This is a string"
'This is also a string'
```

Escape sequences are supported:
- `\"` - Double quote
- `\'` - Single quote
- `\\` - Backslash

---

## Variables

### Variable Declaration

Variables are declared using the `var` keyword:

```
var name = value;
```

### Rules

- Variable names must start with a letter or underscore
- Variable names can contain letters, digits, and underscores
- Variables are case-sensitive (`myVar` ≠ `myvar`)
- Variables must be assigned a value at declaration time

### Examples

```
var x = 42;
var message = "Hello, Eddie!";
var pi = 3.14159;
var isActive = true;
var _private = "underscore start";
```

### Variable Usage

Once declared, variables can be referenced by name:

```
var x = 10;
var y = x + 5;  // y is now 15
```

### Variable Scope

- Variables persist across statements in the same scope
- Inside control flow blocks, variable changes propagate to parent scope
- Each block creates a new interpreter instance, but variables are shared

---

## Operators

Eddie supports the following operators with standard precedence (highest to lowest):

### Arithmetic Operators

| Operator | Name | Example | Result |
|----------|------|---------|--------|
| `+` | Addition | `5 + 3` | `8` |
| `-` | Subtraction | `5 - 3` | `2` |
| `*` | Multiplication | `5 * 3` | `15` |
| `/` | Division | `15 / 3` | `5.0` |

### Comparison Operators

| Operator | Meaning | Example | Result |
|----------|---------|---------|--------|
| `==` | Equal to | `5 == 5` | `true` |
| `=>` | Greater than or equal | `5 => 3` | `true` |
| `=<` | Less than or equal | `3 =< 5` | `true` |

**Note:** Eddie uses `=>` for `>=` and `=<` for `<=`

### Logical Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `and` | Logical AND | `true and false` → `false` |
| `or` | Logical OR | `true or false` → `true` |
| `not(expr)` | Logical NOT | `not(true)` → `false` |

### Operator Precedence

From **highest** to **lowest** precedence:

1. `not()` (unary negation)
2. `*`, `/` (multiplication, division)
3. `+`, `-` (addition, subtraction)
4. `==`, `=>`, `=<` (comparison)
5. `and` (logical AND)
6. `or` (logical OR, lowest precedence)

### Parentheses for Grouping

Use parentheses to override precedence:

```
var result = (2 + 3) * 4;  // Result: 20 (not 14)
```

---

## Control Flow

### If/Else Statement

Execute code conditionally:

```
if (condition) {
  // Code executes if condition is true
}

if (condition) {
  // Code executes if condition is true
} else {
  // Code executes if condition is false
}
```

**Example:**
```
var age = 18;

if (age => 18) {
  var message = "You are an adult";
} else {
  var message = "You are a minor";
}
```

### While Loop

Repeat code while a condition is true:

```
while (condition) {
  // Code executes repeatedly while condition is true
}
```

**Example:**
```
var count = 0;

while (count =< 5) {
  var count = count + 1;
}
```

**Safety Limit:** While loops are limited to 1,000,000 iterations to prevent infinite loops.

### Repeat Loop

Execute code a fixed number of times:

```
repeat (count) {
  // Code executes exactly count times
}
```

**Example:**
```
repeat (3) {
  var x = 1;  // This executes 3 times
}
```

---

## Built-in Functions

### String Functions

#### `join(str1, str2, ...)`

Concatenate multiple strings together.

```
var result = join("Hello", " ", "World");  // "Hello World"
var text = join("A", "B", "C");             // "ABC"
```

#### `letter(index, string)`

Get a single character from a string at 1-indexed position.

```
var first = letter(1, "hello");  // "h"
var third = letter(3, "hello");  // "l"
var out_of_bounds = letter(10, "hello");  // None (no error)
```

**Note:** Indexing starts at 1 (not 0). Out-of-bounds indices return `None`.

#### `len(string)`

Get the length (number of characters) of a string.

```
var length = len("hello");  // 5
var empty = len("");        // 0
```

### Math Functions

#### `random(min, max)`

Generate a random integer between `min` and `max` (inclusive).

```
var dice_roll = random(1, 6);      // Random number 1-6
var coin_flip = random(0, 1);      // 0 or 1
var random_num = random(100, 200); // Random number 100-200
```

### Input/Output Functions

#### `ask(prompt)`

Display a prompt and wait for user input.

```
ask("What is your name? ");
```

#### `answer()`

Retrieve the user input from the most recent `ask()` call.

```
ask("Enter a number: ");
var user_input = answer();  // Stores user's input
```

**Example:**
```
ask("What is your name? ");
var name = answer();
var greeting = join("Hello, ", name);
```

### Timing Functions

#### `wait(seconds)`

Pause execution for a specified number of seconds.

```
wait(2);     // Pause for 2 seconds
wait(0.5);   // Pause for half a second
```

#### `pause(condition)`

Pause execution until a condition becomes true. Polls every 0.1 seconds.

```
var ready = false;
pause(ready == true);  // Wait until ready becomes true
```

#### `timer()`

Start a timer to measure elapsed time.

```
timer();
```

#### `resetTimer()`

Stop the most recent timer and print elapsed time.

```
timer();
wait(2);
resetTimer();  // Prints: Timer 'timer_0' elapsed: 2.00 seconds
```

---

## Comments

Comments in Eddie start with `//` and extend to the end of the line:

```
var x = 5;  // This is a comment
// This entire line is a comment
var y = 10; // Another comment
```

Comments are completely ignored by the interpreter.

---

## Examples

### Example 1: Simple Calculator

```
var a = 10;
var b = 5;
var sum = a + b;
var product = a * b;
```

### Example 2: User Interaction

```
ask("What is your favorite number? ");
var favorite = answer();
var doubled = favorite * 2;
```

### Example 3: Conditional Logic

```
var score = 85;

if (score => 90) {
  var grade = "A";
} else {
  if (score => 80) {
    var grade = "B";
  } else {
    var grade = "C";
  }
}
```

### Example 4: Counting Loop

```
var sum = 0;
var i = 1;

while (i =< 10) {
  var sum = sum + i;
  var i = i + 1;
}
```

### Example 5: Repeat Pattern

```
repeat (5) {
  var roll = random(1, 6);
}
```

### Example 6: Timer Measurement

```
timer();
wait(3);
resetTimer();  // Shows elapsed time (approximately 3 seconds)
```

### Example 7: String Manipulation

```
var first_name = "John";
var last_name = "Doe";
var full_name = join(first_name, " ", last_name);

var length = len(full_name);
var first_letter = letter(1, first_name);  // "J"
```

---

## Error Handling

The Eddie interpreter provides error messages for common issues:

| Error Type | Cause | Example |
|-----------|-------|---------|
| **SyntaxError** | Invalid syntax | Missing `{` or `}` |
| **NameError** | Undefined variable or function | `x` used before declaration |
| **ValueError** | Wrong number of function arguments | `random(1)` (needs 2 args) |
| **RuntimeError** | Division by zero or exceeded limits | `5 / 0` or infinite loop |

---

## Tips and Best Practices

1. **Always end statements with semicolons** - This is required in Eddie
2. **Use meaningful variable names** - `user_age` is better than `ua`
3. **Comment complex logic** - Help future readers understand your code
4. **Test incrementally** - Build and test small pieces before combining
5. **Use while loop safely** - Set clear exit conditions to avoid infinite loops
6. **Remember 1-indexed strings** - `letter()` uses position 1, not 0

---

## Reserved Keywords

The following words are reserved and cannot be used as variable names:

```
var if else while repeat wait pause ask answer timer resetTimer
true false and or not
```

---

## Limitations and Notes

- **Maximum while loop iterations:** 1,000,000
- **Maximum pause polls:** 1,000,000
- **String indexing:** Starts at 1 (not 0)
- **Out-of-bounds string access:** Returns `None` (no error thrown)
- **Variable scope:** Variables persist in parent scope when modified in blocks
- **Division result:** Always returns a float (e.g., `4 / 2` = `2.0`)

---

## Quick Reference

### Variable Declaration
```
var name = value;
```

### Control Flow Keywords
```
if (condition) { ... } else { ... }
while (condition) { ... }
repeat (count) { ... }
```

### Operators
```
+ - * / == => =< and or not()
```

### Built-in Functions
```
random(min, max)
join(str1, str2, ...)
letter(index, string)
len(string)
ask(prompt)
answer()
wait(seconds)
pause(condition)
timer()
resetTimer()
```

---

**Happy Eddie programming!** 🎉
