#!/usr/bin/env python3
"""
Eddie Language Interpreter
A simple DIY language interpreter supporting variables, control flow, and built-in functions.

Syntax Features:
  - Variables: var name = value;
  - Operators: +, -, *, /, ==, =>, =<
  - Control Flow: if/else, while, repeat
  - Built-in Functions: random, join, letter, len, ask, answer, wait, pause, timer, resetTimer
  - Comments: // comment
"""

import sys
import re
import time
import random
from typing import Any, Dict, List, Optional


class EddieInterpreter:
    """Main interpreter class for Eddie language execution."""

    def __init__(self):
        """Initialize the interpreter with empty state."""
        self.variables: Dict[str, Any] = {}  # Store variable values
        self.timers: Dict[str, float] = {}  # Store active timer start times
        self.user_input: Optional[str] = None  # Store last user input from ask()
        self.token_index = 0  # Current position in token stream
        self.tokens: List[str] = []  # List of tokens to parse

    # ============================================================================
    # TOKENIZATION: Convert raw code string into token stream
    # ============================================================================

    def tokenize(self, code: str) -> List[str]:
        """
        Convert Eddie language code into a list of tokens.
        
        Process:
          1. Remove comments (// ... end of line)
          2. Use regex to extract tokens: strings, operators, keywords, identifiers, numbers
          3. Filter out empty tokens
        
        Args:
            code (str): Raw Eddie language source code
            
        Returns:
            List[str]: List of tokens ready for parsing
        """
        # Remove comments (everything from // to end of line)
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)

        # Define regex pattern for tokenization
        # Matches: strings, parentheses, braces, semicolons, commas, operators, keywords/ids, numbers
        token_pattern = r'''
            "(?:\\.|[^"\\])*"  |  # Double-quoted strings with escape support
            '(?:\\.|[^'\\])*'  |  # Single-quoted strings with escape support
            \(                  |  # Left parenthesis
            \)                  |  # Right parenthesis
            \{                  |  # Left brace
            \}                  |  # Right brace
            \;                  |  # Semicolon
            \,                  |  # Comma
            =>                  |  # Greater-than-or-equal operator
            =<                  |  # Less-than-or-equal operator
            ==                  |  # Equality operator
            \+                  |  # Plus operator
            \-                  |  # Minus operator
            \*                  |  # Multiplication operator
            \/                  |  # Division operator
            [a-zA-Z_]\w*        |  # Identifiers and keywords (start with letter/underscore)
            \d+\.?\d*              # Numbers (integers and floats)
        '''

        tokens = re.findall(token_pattern, code, re.VERBOSE)
        # Strip whitespace from each token and filter out empty tokens
        return [t.strip() for t in tokens if t.strip()]

    # ============================================================================
    # TOKEN STREAM NAVIGATION: Move through tokens and check current position
    # ============================================================================

    def current_token(self) -> Optional[str]:
        """Get token at current position without advancing."""
        if self.token_index < len(self.tokens):
            return self.tokens[self.token_index]
        return None

    def peek_token(self, offset: int = 1) -> Optional[str]:
        """Peek ahead in token stream by offset positions."""
        idx = self.token_index + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return None

    def advance(self) -> Optional[str]:
        """Get current token and move to next position."""
        token = self.current_token()
        self.token_index += 1
        return token

    def expect(self, expected_token: str) -> bool:
        """
        Check if current token matches expected token, advance if it does.
        
        Args:
            expected_token (str): The token we expect to see
            
        Returns:
            bool: True if token matched and advanced, False otherwise
        """
        if self.current_token() == expected_token:
            self.advance()
            return True
        return False

    # ============================================================================
    # MAIN PARSING: Entry point for statement parsing
    # ============================================================================

    def parse(self, tokens: List[str]) -> None:
        """
        Parse and execute a list of tokens.
        
        Loops through tokens and identifies statement types (var, if, while, etc.)
        and delegates to appropriate parser method.
        
        Args:
            tokens (List[str]): Tokens to parse
        """
        self.tokens = tokens
        self.token_index = 0

        # Process tokens one statement at a time
        while self.token_index < len(self.tokens):
            self.parse_statement()

    def parse_statement(self) -> None:
        """
        Parse a single statement and dispatch to appropriate handler.
        
        Recognizes:
          - var: Variable declaration
          - if: Conditional statement
          - while: While loop
          - repeat: Fixed-count loop
          - wait: Sleep/pause
          - pause: Wait until condition
          - ask: User input prompt
          - timer/resetTimer: Timer operations
          - Unknown tokens are skipped (error recovery)
        """
        token = self.current_token()

        if token is None:
            return
        elif token == 'var':
            self.parse_var_declaration()
        elif token == 'if':
            self.parse_if_statement()
        elif token == 'while':
            self.parse_while_statement()
        elif token == 'repeat':
            self.parse_repeat_statement()
        elif token == 'wait':
            self.parse_wait_statement()
        elif token == 'pause':
            self.parse_pause_statement()
        elif token == 'ask':
            self.parse_ask_statement()
        elif token == 'timer':
            self.parse_timer_statement()
        elif token == 'resetTimer':
            self.parse_reset_timer_statement()
        else:
            # Unknown token - skip it (error recovery for robustness)
            self.advance()

    # ============================================================================
    # VARIABLE DECLARATION: Parse "var name = expression;"
    # ============================================================================

    def parse_var_declaration(self) -> None:
        """
        Parse variable declaration: var name = expression;
        
        Syntax:
          var identifier = expression;
        
        Raises:
          SyntaxError: If syntax is invalid or name is not a valid identifier
          
        Example:
          var x = 5;
          var message = "hello";
          var result = 3 + 4 * 2;
        """
        self.expect('var')

        # Get variable name
        name = self.advance()
        if not name or not (name[0].isalpha() or name[0] == '_'):
            raise SyntaxError(f"Invalid variable name: {name}. Must start with letter or underscore.")

        # Expect '=' assignment operator
        if not self.expect('='):
            raise SyntaxError(f"Expected '=' after variable name '{name}'")

        # Parse and evaluate the expression
        value = self.parse_expression()

        # Consume optional semicolon
        self.expect(';')

        # Store variable in global state
        self.variables[name] = value

    # ============================================================================
    # EXPRESSION PARSING: Operator precedence using recursive descent
    # ============================================================================

    def parse_expression(self) -> Any:
        """
        Parse an expression with proper operator precedence.
        
        Uses recursive descent parsing to handle precedence:
          1. or (lowest precedence)
          2. and
          3. comparison (==, =>, =<)
          4. additive (+, -)
          5. multiplicative (*, /)
          6. unary (not)
          7. primary (highest precedence)
        
        Returns:
            Any: Evaluated result of the expression
        """
        return self.parse_or_expression()

    def parse_or_expression(self) -> Any:
        """Parse logical OR expressions (lowest precedence)."""
        left = self.parse_and_expression()

        while self.current_token() == 'or':
            self.advance()
            right = self.parse_and_expression()
            left = left or right  # Short-circuit OR

        return left

    def parse_and_expression(self) -> Any:
        """Parse logical AND expressions."""
        left = self.parse_comparison_expression()

        while self.current_token() == 'and':
            self.advance()
            right = self.parse_comparison_expression()
            left = left and right  # Short-circuit AND

        return left

    def parse_comparison_expression(self) -> Any:
        """Parse comparison expressions: ==, =>, =<"""
        left = self.parse_additive_expression()

        while self.current_token() in ['==', '=>', '=<']:
            op = self.advance()
            right = self.parse_additive_expression()

            if op == '==':
                left = left == right
            elif op == '=>':
                # Note: Eddie uses => for >= (greater-than-or-equal)
                left = left >= right
            elif op == '=<':
                # Note: Eddie uses =< for <= (less-than-or-equal)
                left = left <= right

        return left

    def parse_additive_expression(self) -> Any:
        """Parse addition and subtraction expressions."""
        left = self.parse_multiplicative_expression()

        while self.current_token() in ['+', '-']:
            op = self.advance()
            right = self.parse_multiplicative_expression()

            if op == '+':
                left = left + right
            elif op == '-':
                left = left - right

        return left

    def parse_multiplicative_expression(self) -> Any:
        """Parse multiplication and division expressions."""
        left = self.parse_unary_expression()

        while self.current_token() in ['*', '/']:
            op = self.advance()
            right = self.parse_unary_expression()

            if op == '*':
                left = left * right
            elif op == '/':
                # Validate to prevent division by zero
                if right == 0:
                    raise RuntimeError("Division by zero error")
                left = left / right

        return left

    def parse_unary_expression(self) -> Any:
        """Parse unary expressions like not()."""
        token = self.current_token()

        if token == 'not':
            self.advance()
            if not self.expect('('):
                raise SyntaxError("Expected '(' after 'not'")
            result = self.parse_expression()
            if not self.expect(')'):
                raise SyntaxError("Expected ')' to close 'not'")
            # Logical negation
            return not result

        return self.parse_primary_expression()

    def parse_primary_expression(self) -> Any:
        """
        Parse primary expressions (atoms of expressions):
          - String literals: "hello" or 'hello'
          - Number literals: 42 or 3.14
          - Boolean literals: true, false
          - Variable references: myVar
          - Function calls: random(1, 10)
          - Parenthesized expressions: (1 + 2)
        
        Returns:
            Any: The evaluated value of the primary expression
        """
        token = self.current_token()

        if token is None:
            raise SyntaxError("Unexpected end of input in expression")

        # ===== STRING LITERALS =====
        if token.startswith('"') or token.startswith("'"):
            self.advance()
            # Remove surrounding quotes
            return token[1:-1]

        # ===== NUMBER LITERALS =====
        try:
            num = float(token)
            self.advance()
            # Convert to int if no decimal part
            return int(num) if num == int(num) else num
        except ValueError:
            pass

        # ===== IDENTIFIERS: Variables, Keywords, or Function Calls =====
        if token and (token[0].isalpha() or token[0] == '_'):
            name = self.advance()

            # Check if it's a function call (followed by '(')
            if self.current_token() == '(':
                return self.parse_function_call(name)

            # Check for built-in boolean values
            if name in ['true', 'True']:
                return True
            if name in ['false', 'False']:
                return False

            # Check if variable exists
            if name in self.variables:
                return self.variables[name]

            # Undefined variable - raise error
            raise NameError(f"Undefined variable: '{name}'")

        # ===== PARENTHESIZED EXPRESSIONS =====
        if token == '(':
            self.advance()
            result = self.parse_expression()
            if not self.expect(')'):
                raise SyntaxError("Expected ')' to close parenthesized expression")
            return result

        raise SyntaxError(f"Unexpected token in expression: '{token}'")

    # ============================================================================
    # FUNCTION CALLS: Parse and execute function calls
    # ============================================================================

    def parse_function_call(self, func_name: str) -> Any:
        """
        Parse a function call: function(arg1, arg2, ...)
        
        Args:
            func_name (str): Name of the function being called
            
        Returns:
            Any: Return value of the built-in function
            
        Raises:
            SyntaxError: If function call syntax is invalid
        """
        if not self.expect('('):
            raise SyntaxError(f"Expected '(' after function name '{func_name}'")

        args = []

        # Parse comma-separated arguments
        while self.current_token() != ')':
            args.append(self.parse_expression())

            if self.current_token() == ',':
                self.advance()
            elif self.current_token() != ')':
                raise SyntaxError(f"Expected ',' or ')' in function call to '{func_name}'")

        if not self.expect(')'):
            raise SyntaxError(f"Expected ')' to close function call to '{func_name}'")

        # Execute built-in function
        return self.call_builtin(func_name, args)

    def call_builtin(self, name: str, args: List[Any]) -> Any:
        """
        Execute a built-in function.
        
        Implemented functions:
          - random(min, max): Generate random integer in range
          - join(str1, str2, ...): Concatenate strings
          - letter(index, string): Get character at 1-indexed position
          - len(string): Get string length
          - answer(): Get last user input from ask()
        
        Args:
            name (str): Function name
            args (List[Any]): Function arguments
            
        Returns:
            Any: Function result
            
        Raises:
            ValueError: If wrong number of arguments
            NameError: If function is undefined
        """
        if name == 'random':
            # random(min, max) - returns random integer between min and max inclusive
            if len(args) != 2:
                raise ValueError(f"random() expects 2 arguments, got {len(args)}")
            return random.randint(int(args[0]), int(args[1]))

        elif name == 'join':
            # join(str1, str2, ...) - concatenates all arguments as strings
            return ''.join(str(arg) for arg in args)

        elif name == 'letter':
            # letter(index, string) - returns character at 1-indexed position
            if len(args) != 2:
                raise ValueError(f"letter() expects 2 arguments, got {len(args)}")
            index = int(args[0]) - 1  # Convert from 1-indexed to 0-indexed
            string = str(args[1])
            if 0 <= index < len(string):
                return string[index]
            # Index out of bounds returns None
            return None

        elif name == 'len':
            # len(string) - returns length of string
            if len(args) != 1:
                raise ValueError(f"len() expects 1 argument, got {len(args)}")
            return len(str(args[0]))

        elif name == 'answer':
            # answer() - returns last user input from ask()
            return self.user_input

        else:
            raise NameError(f"Undefined function: '{name}'")

    # ============================================================================
    # CONTROL FLOW: if/else, while, repeat statements
    # ============================================================================

    def _extract_block_tokens(self) -> List[str]:
        """
        Extract tokens from opening brace to matching closing brace.
        Assumes current token is the opening brace.
        
        Returns:
            List[str]: Tokens inside the braces (excluding braces)
            
        Raises:
            SyntaxError: If braces don't match
        """
        if not self.expect('{'):
            raise SyntaxError("Expected '{' to start block")

        # Find matching closing brace
        block_start = self.token_index
        brace_count = 1

        while brace_count > 0 and self.token_index < len(self.tokens):
            token = self.current_token()
            if token == '{':
                brace_count += 1
            elif token == '}':
                brace_count -= 1

            if brace_count > 0:
                self.token_index += 1

        if brace_count != 0:
            raise SyntaxError("Mismatched braces - expected closing '}'")

        block_end = self.token_index
        block_tokens = self.tokens[block_start:block_end]

        if not self.expect('}'):
            raise SyntaxError("Expected '}' to close block")

        return block_tokens

    def parse_if_statement(self) -> None:
        """
        Parse if/else statement: if (condition) { ... } [else { ... }]
        
        Syntax:
          if (expression) {
            statements
          }
          
          if (expression) {
            statements
          } else {
            statements
          }
        
        Note:
          - Condition is evaluated once at parse time
          - Creates new interpreter instance for block scope
          - Variables modified in block are preserved in parent scope
        """
        if not self.expect('if'):
            raise SyntaxError("Expected 'if'")

        if not self.expect('('):
            raise SyntaxError("Expected '(' after 'if'")

        # Evaluate the condition
        condition = self.parse_expression()

        if not self.expect(')'):
            raise SyntaxError("Expected ')' after if condition")

        # Extract the if block
        block_tokens = self._extract_block_tokens()

        # Execute if block if condition is true
        if condition:
            interpreter = EddieInterpreter()
            interpreter.variables = self.variables.copy()  # FIX: Copy variables to avoid mutations
            interpreter.parse(block_tokens)
            self.variables = interpreter.variables
        else:
            # Check for else clause
            if self.current_token() == 'else':
                self.advance()
                else_block_tokens = self._extract_block_tokens()

                # Execute else block
                interpreter = EddieInterpreter()
                interpreter.variables = self.variables.copy()  # FIX: Copy variables
                interpreter.parse(else_block_tokens)
                self.variables = interpreter.variables

    def parse_while_statement(self) -> None:
        """
        Parse while loop: while (condition) { ... }
        
        Syntax:
          while (expression) {
            statements
          }
        
        Behavior:
          - Condition is re-evaluated on each iteration
          - Loop terminates when condition becomes false
          - Infinite loop protection: MAX_ITERATIONS safety limit
        
        Note:
          - Variables are shared across iterations
        """
        if not self.expect('while'):
            raise SyntaxError("Expected 'while'")

        if not self.expect('('):
            raise SyntaxError("Expected '(' after 'while'")

        # Extract condition tokens
        condition_tokens = self._extract_condition_tokens()

        if not self.expect(')'):
            raise SyntaxError("Expected ')' after while condition")

        if not self.expect('{'):
            raise SyntaxError("Expected '{' to start while block")

        # Extract loop body
        block_tokens = self._extract_block_tokens()

        # Execute while loop
        iteration_count = 0
        MAX_ITERATIONS = 1000000  # Safety limit to prevent infinite loops

        while iteration_count < MAX_ITERATIONS:
            iteration_count += 1

            # Re-evaluate condition on each iteration
            cond_interpreter = EddieInterpreter()
            cond_interpreter.variables = self.variables.copy()
            cond_interpreter.tokens = condition_tokens
            cond_interpreter.token_index = 0
            condition = cond_interpreter.parse_expression()
            self.variables = cond_interpreter.variables

            # Exit loop if condition is false
            if not condition:
                break

            # Execute loop body
            interpreter = EddieInterpreter()
            interpreter.variables = self.variables.copy()
            interpreter.parse(block_tokens)
            self.variables = interpreter.variables

        if iteration_count >= MAX_ITERATIONS:
            raise RuntimeError(f"While loop exceeded maximum iterations ({MAX_ITERATIONS})")

    def _extract_condition_tokens(self) -> List[str]:
        """
        Extract tokens representing a condition enclosed in parentheses.
        Current token should be first token of condition.
        
        Returns:
            List[str]: Condition tokens (excluding surrounding parentheses)
        """
        condition_tokens = []
        paren_count = 1

        while paren_count > 0 and self.current_token() is not None:
            token = self.current_token()

            if token == '(':
                paren_count += 1
            elif token == ')':
                paren_count -= 1
                if paren_count == 0:
                    break

            condition_tokens.append(token)
            self.advance()

        return condition_tokens

    def parse_repeat_statement(self) -> None:
        """
        Parse repeat loop: repeat (count) { ... }
        
        Syntax:
          repeat (integer_expression) {
            statements
          }
        
        Behavior:
          - Count is evaluated once at parse time
          - Loop body executes count times
          - Count must be a positive integer
        
        Example:
          repeat (5) { var x = 1; }  // Executes block 5 times
        """
        if not self.expect('repeat'):
            raise SyntaxError("Expected 'repeat'")

        if not self.expect('('):
            raise SyntaxError("Expected '(' after 'repeat'")

        # Evaluate repeat count
        count = int(self.parse_expression())

        if not self.expect(')'):
            raise SyntaxError("Expected ')' after repeat count")

        # Extract loop body
        block_tokens = self._extract_block_tokens()

        # Execute repeat loop
        for i in range(count):
            interpreter = EddieInterpreter()
            interpreter.variables = self.variables.copy()
            interpreter.parse(block_tokens)
            self.variables = interpreter.variables

    # ============================================================================
    # TIMING FUNCTIONS: wait, pause, timer, resetTimer
    # ============================================================================

    def parse_wait_statement(self) -> None:
        """
        Parse wait statement: wait(seconds);
        
        Causes execution to pause for specified number of seconds.
        
        Syntax:
          wait(seconds_expression);
        
        Example:
          wait(2.5);     // Pause for 2.5 seconds
          wait(1);       // Pause for 1 second
        """
        if not self.expect('wait'):
            raise SyntaxError("Expected 'wait'")

        if not self.expect('('):
            raise SyntaxError("Expected '(' after 'wait'")

        # Evaluate duration in seconds
        seconds = float(self.parse_expression())

        if not self.expect(')'):
            raise SyntaxError("Expected ')' after wait duration")

        self.expect(';')

        # Pause execution
        if seconds > 0:
            time.sleep(seconds)

    def parse_pause_statement(self) -> None:
        """
        Parse pause statement: pause(condition);
        
        Pauses execution until the condition becomes true.
        Useful for waiting for user input or state changes.
        
        Syntax:
          pause(boolean_expression);
        
        Example:
          pause(x == 5);          // Wait until x equals 5
          pause(not(isEmpty));    // Wait until isEmpty is false
        
        Note:
          - Polls condition every 0.1 seconds
          - MAX_POLLS safety limit prevents infinite pause
        """
        if not self.expect('pause'):
            raise SyntaxError("Expected 'pause'")

        if not self.expect('('):
            raise SyntaxError("Expected '(' after 'pause'")

        # Extract condition tokens
        condition_tokens = self._extract_condition_tokens()

        if not self.expect(')'):
            raise SyntaxError("Expected ')' after pause condition")

        self.expect(';')

        # Wait until condition becomes true
        poll_count = 0
        MAX_POLLS = 1000000  # Safety limit

        while poll_count < MAX_POLLS:
            poll_count += 1

            # Re-evaluate condition
            cond_interpreter = EddieInterpreter()
            cond_interpreter.variables = self.variables.copy()
            cond_interpreter.tokens = condition_tokens
            cond_interpreter.token_index = 0
            condition = cond_interpreter.parse_expression()
            self.variables = cond_interpreter.variables

            # Exit if condition is true
            if condition:
                break

            # Poll every 0.1 seconds to reduce CPU usage
            time.sleep(0.1)

        if poll_count >= MAX_POLLS:
            raise RuntimeError(f"Pause exceeded maximum poll count ({MAX_POLLS})")

    def parse_ask_statement(self) -> None:
        """
        Parse ask statement: ask(prompt_string);
        
        Prompts user for input and stores result in internal buffer.
        Retrieved with answer() function.
        
        Syntax:
          ask(string_expression);
        
        Example:
          ask("What is your name? ");
          var name = answer();
        
        Note:
          - Input is stored as string
          - Use answer() to retrieve the input
          - Only one input buffer (subsequent ask() overwrites previous)
        """
        if not self.expect('ask'):
            raise SyntaxError("Expected 'ask'")

        if not self.expect('('):
            raise SyntaxError("Expected '(' after 'ask'")

        # Evaluate prompt expression
        prompt = self.parse_expression()

        if not self.expect(')'):
            raise SyntaxError("Expected ')' after ask prompt")

        self.expect(';')

        # Prompt user and store input
        self.user_input = input(str(prompt))

    def parse_timer_statement(self) -> None:
        """
        Parse timer statement: timer();
        
        Starts a new timer and records current time.
        Used with resetTimer() to measure elapsed time.
        
        Syntax:
          timer();
        
        Example:
          timer();
          wait(2);
          resetTimer();  // Prints elapsed time
        
        Note:
          - Multiple timers can be created
          - resetTimer() resets the most recent timer
        """
        if not self.expect('timer'):
            raise SyntaxError("Expected 'timer'")

        if not self.expect('('):
            raise SyntaxError("Expected '(' after 'timer'")

        if not self.expect(')'):
            raise SyntaxError("Expected ')' to close timer()")

        self.expect(';')

        # Create new timer with unique ID
        timer_id = f"timer_{len(self.timers)}"
        self.timers[timer_id] = time.time()
        print(f"Timer started: {timer_id}")

    def parse_reset_timer_statement(self) -> None:
        """
        Parse resetTimer statement: resetTimer();
        
        Stops the most recent timer and prints elapsed time.
        
        Syntax:
          resetTimer();
        
        Example:
          timer();
          wait(2.5);
          resetTimer();  // Output: Timer 'timer_0' elapsed: 2.50 seconds
        
        Note:
          - Resets most recent (last created) timer
          - Prints elapsed time in seconds with 2 decimal places
          - Warning if no active timers
        """
        if not self.expect('resetTimer'):
            raise SyntaxError("Expected 'resetTimer'")

        if not self.expect('('):
            raise SyntaxError("Expected '(' after 'resetTimer'")

        if not self.expect(')'):
            raise SyntaxError("Expected ')' to close resetTimer()")

        self.expect(';')

        # Stop most recent timer and display elapsed time
        if self.timers:
            timer_id = list(self.timers.keys())[-1]
            elapsed = time.time() - self.timers[timer_id]
            print(f"Timer '{timer_id}' elapsed: {elapsed:.2f} seconds")
            del self.timers[timer_id]
        else:
            print("Warning: No active timers to reset")

    # ============================================================================
    # FILE AND REPL MODE: Main entry points for execution
    # ============================================================================

    def run_file(self, filename: str) -> None:
        """
        Run an Eddie language script from a file.
        
        Args:
            filename (str): Path to the .txt file containing Eddie code
            
        Raises:
            FileNotFoundError: If file doesn't exist
            SyntaxError: If code has syntax errors
            RuntimeError: If code execution fails
        """
        try:
            # Read file contents
            with open(filename, 'r') as f:
                code = f.read()

            # Tokenize and parse
            tokens = self.tokenize(code)
            self.parse(tokens)

        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    def run_repl(self) -> None:
        """
        Run interactive Read-Eval-Print Loop (REPL) mode.
        
        Features:
          - Prompt for input: "eddie> "
          - Execute each line as it's entered
          - Type 'exit' to quit
          - Type 'help' for command reference
          - Error handling: Print errors and continue
          - Keyboard interrupt: Graceful shutdown with Ctrl+C
        """
        print("=" * 60)
        print("Eddie Language REPL v1.0")
        print("=" * 60)
        print("Type 'exit' to quit, 'help' for command list")
        print()

        while True:
            try:
                # Prompt for input
                line = input("eddie> ").strip()

                # Check for exit command
                if line.lower() == 'exit':
                    print("Goodbye!")
                    break

                # Check for help command
                if line.lower() == 'help':
                    print("""
Available commands:
  var x = value;                 - Create variable
  if (cond) { ... }              - Conditional
  while (cond) { ... }           - While loop
  repeat (n) { ... }             - Repeat N times
  wait(seconds);                 - Sleep
  ask("prompt");                 - Get user input
  answer();                      - Get last input
  timer();                       - Start timer
  resetTimer();                  - Stop timer
  exit                           - Quit REPL
  help                           - Show this help
                    """)
                    continue

                # Skip empty lines
                if not line:
                    continue

                # Tokenize and execute
                tokens = self.tokenize(line)
                if tokens:
                    self.parse(tokens)

            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                print("\n[Interrupted by user]")
                break
            except Exception as e:
                # Print error but continue REPL
                print(f"Error: {e}")


def main():
    """
    Main entry point for Eddie language interpreter.
    
    Modes:
      1. File mode: python3 eddie-interpreter.py filename.txt
      2. REPL mode: python3 eddie-interpreter.py (no arguments)
    """
    interpreter = EddieInterpreter()

    if len(sys.argv) > 1:
        # FILE MODE: Execute file
        filename = sys.argv[1]
        interpreter.run_file(filename)
    else:
        # REPL MODE: Interactive shell
        interpreter.run_repl()


if __name__ == '__main__':
    main()
