#!/usr/bin/env python3
"""
Eddie Language Interpreter
A simple DIY language interpreter supporting variables, control flow, and built-in functions.
"""

import sys
import re
import time
import random
from typing import Any, Dict, List, Tuple, Optional

class EddieInterpreter:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.timers: Dict[str, float] = {}
        self.user_input: Optional[str] = None
        self.token_index = 0
        self.tokens: List[str] = []
        
    def tokenize(self, code: str) -> List[str]:
        """Tokenize eddie-lang code into manageable pieces."""
        # Remove comments
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        
        # Tokenize while preserving strings and operators
        token_pattern = r'''
            "(?:\\.|[^"\\])*"  |  # String literals
            '(?:\\.|[^'\\])*'  |  # String literals
            \(                  |  # Parentheses
            \)                  |
            \{                  |  # Braces
            \}                  |
            \;                  |  # Semicolon
            \,                  |  # Comma
            =>                  |  # Greater than or equal
            =<                  |  # Less than or equal
            ==                  |  # Equality
            \+                  |  # Operators
            \-                  |
            \*                  |
            \/                  |
            [a-zA-Z_]\w*        |  # Identifiers and keywords
            \d+\.?\d*              # Numbers
        '''
        
        tokens = re.findall(token_pattern, code, re.VERBOSE)
        return [t.strip() for t in tokens if t.strip()]
    
    def parse(self, tokens: List[str]) -> None:
        """Parse and execute tokens."""
        self.tokens = tokens
        self.token_index = 0
        
        while self.token_index < len(self.tokens):
            self.parse_statement()
    
    def current_token(self) -> Optional[str]:
        """Get current token without advancing."""
        if self.token_index < len(self.tokens):
            return self.tokens[self.token_index]
        return None
    
    def peek_token(self, offset: int = 1) -> Optional[str]:
        """Peek ahead in token stream."""
        idx = self.token_index + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return None
    
    def advance(self) -> Optional[str]:
        """Get current token and advance."""
        token = self.current_token()
        self.token_index += 1
        return token
    
    def expect(self, token: str) -> bool:
        """Expect a specific token."""
        if self.current_token() == token:
            self.advance()
            return True
        return False
    
    def parse_statement(self) -> None:
        """Parse a single statement."""
        token = self.current_token()
        
        if token is None:
            return
        
        if token == 'var':
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
            # Skip unknown tokens
            self.advance()
    
    def parse_var_declaration(self) -> None:
        """Parse: var name = expression;"""
        self.expect('var')
        
        name = self.advance()
        if not name or not name[0].isalpha():
            raise SyntaxError(f"Invalid variable name: {name}")
        
        if not self.expect('='):
            raise SyntaxError("Expected '=' in variable declaration")
        
        value = self.parse_expression()
        self.expect(';')
        
        self.variables[name] = value
    
    def parse_expression(self) -> Any:
        """Parse expressions with operator precedence."""
        return self.parse_or_expression()
    
    def parse_or_expression(self) -> Any:
        """Parse logical OR expressions."""
        left = self.parse_and_expression()
        
        while self.current_token() in ['or']:
            op = self.advance()
            right = self.parse_and_expression()
            left = left or right
        
        return left
    
    def parse_and_expression(self) -> Any:
        """Parse logical AND expressions."""
        left = self.parse_comparison_expression()
        
        while self.current_token() in ['and']:
            op = self.advance()
            right = self.parse_comparison_expression()
            left = left and right
        
        return left
    
    def parse_comparison_expression(self) -> Any:
        """Parse comparison expressions."""
        left = self.parse_additive_expression()
        
        while self.current_token() in ['==', '=>', '=<']:
            op = self.advance()
            right = self.parse_additive_expression()
            
            if op == '==':
                left = left == right
            elif op == '=>':
                left = left >= right
            elif op == '=<':
                left = left <= right
        
        return left
    
    def parse_additive_expression(self) -> Any:
        """Parse addition and subtraction."""
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
        """Parse multiplication and division."""
        left = self.parse_unary_expression()
        
        while self.current_token() in ['*', '/']:
            op = self.advance()
            right = self.parse_unary_expression()
            
            if op == '*':
                left = left * right
            elif op == '/':
                if right == 0:
                    raise RuntimeError("Division by zero")
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
            return not result
        
        return self.parse_primary_expression()
    
    def parse_primary_expression(self) -> Any:
        """Parse primary expressions (literals, variables, function calls)."""
        token = self.current_token()
        
        if token is None:
            raise SyntaxError("Unexpected end of input")
        
        # String literal
        if token.startswith('"') or token.startswith("'"):
            self.advance()
            return token[1:-1]  # Remove quotes
        
        # Number literal
        try:
            num = float(token)
            self.advance()
            return int(num) if num == int(num) else num
        except ValueError:
            pass
        
        # Function call or variable
        if token[0].isalpha() or token[0] == '_':
            name = self.advance()
            
            # Check if it's a function call
            if self.current_token() == '(':
                return self.parse_function_call(name)
            
            # It's a variable
            if name in self.variables:
                return self.variables[name]
            elif name in ['true', 'True']:
                return True
            elif name in ['false', 'False']:
                return False
            else:
                raise NameError(f"Undefined variable: {name}")
        
        # Parenthesized expression
        if token == '(':
            self.advance()
            result = self.parse_expression()
            if not self.expect(')'):
                raise SyntaxError("Expected ')' to close expression")
            return result
        
        raise SyntaxError(f"Unexpected token: {token}")
    
    def parse_function_call(self, func_name: str) -> Any:
        """Parse and execute function calls."""
        if not self.expect('('):
            raise SyntaxError(f"Expected '(' after function name {func_name}")
        
        args = []
        
        # Parse arguments
        while self.current_token() != ')':
            args.append(self.parse_expression())
            
            if self.current_token() == ',':
                self.advance()
            elif self.current_token() != ')':
                raise SyntaxError("Expected ',' or ')' in function call")
        
        if not self.expect(')'):
            raise SyntaxError("Expected ')' to close function call")
        
        # Execute built-in functions
        return self.call_builtin(func_name, args)
    
    def call_builtin(self, name: str, args: List[Any]) -> Any:
        """Execute built-in functions."""
        if name == 'random':
            if len(args) != 2:
                raise ValueError(f"random() expects 2 arguments, got {len(args)}")
            return random.randint(int(args[0]), int(args[1]))
        
        elif name == 'join':
            return ''.join(str(arg) for arg in args)
        
        elif name == 'letter':
            if len(args) != 2:
                raise ValueError(f"letter() expects 2 arguments, got {len(args)}")
            index = int(args[0]) - 1  # 1-indexed
            string = str(args[1])
            if 0 <= index < len(string):
                return string[index]
            return None
        
        elif name == 'len':
            if len(args) != 1:
                raise ValueError(f"len() expects 1 argument, got {len(args)}")
            return len(str(args[0]))
        
        elif name == 'answer':
            return self.user_input
        
        else:
            raise NameError(f"Undefined function: {name}")
    
    def parse_if_statement(self) -> None:
        """Parse: if (condition) { ... } or if (condition) { ... } else { ... }"""
        if not self.expect('if'):
            raise SyntaxError("Expected 'if'")
        
        if not self.expect('('):
            raise SyntaxError("Expected '(' after 'if'")
        
        condition = self.parse_expression()
        
        if not self.expect(')'):
            raise SyntaxError("Expected ')' after condition")
        
        if not self.expect('{'):
            raise SyntaxError("Expected '{' to start if block")
        
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
        
        block_end = self.token_index
        block_tokens = self.tokens[block_start:block_end]
        
        if not self.expect('}'):
            raise SyntaxError("Expected '}' to close if block")
        
        # Execute if block if condition is true
        if condition:
            interpreter = EddieInterpreter()
            interpreter.variables = self.variables
            interpreter.parse(block_tokens)
            self.variables = interpreter.variables
        else:
            # Check for else
            if self.current_token() == 'else':
                self.advance()
                if not self.expect('{'):
                    raise SyntaxError("Expected '{' after 'else'")
                
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
                
                block_end = self.token_index
                block_tokens = self.tokens[block_start:block_end]
                
                if not self.expect('}'):
                    raise SyntaxError("Expected '}' to close else block")
                
                interpreter = EddieInterpreter()
                interpreter.variables = self.variables
                interpreter.parse(block_tokens)
                self.variables = interpreter.variables
    
    def parse_while_statement(self) -> None:
        """Parse: while (condition) { ... }"""
        if not self.expect('while'):
            raise SyntaxError("Expected 'while'")
        
        if not self.expect('('):
            raise SyntaxError("Expected '(' after 'while'")
        
        # Save position for re-evaluation
        condition_start = self.token_index
        
        # Find the condition tokens
        paren_count = 1
        condition_tokens = []
        while paren_count > 0:
            token = self.current_token()
            if token == '(':
                paren_count += 1
            elif token == ')':
                paren_count -= 1
                if paren_count == 0:
                    break
            condition_tokens.append(token)
            self.advance()
        
        if not self.expect(')'):
            raise SyntaxError("Expected ')' after condition")
        
        if not self.expect('{'):
            raise SyntaxError("Expected '{' to start while block")
        
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
        
        block_end = self.token_index
        block_tokens = self.tokens[block_start:block_end]
        
        if not self.expect('}'):
            raise SyntaxError("Expected '}' to close while block")
        
        # Execute while loop
        while True:
            # Evaluate condition
            cond_interpreter = EddieInterpreter()
            cond_interpreter.variables = self.variables
            cond_interpreter.tokens = condition_tokens
            cond_interpreter.token_index = 0
            condition = cond_interpreter.parse_expression()
            self.variables = cond_interpreter.variables
            
            if not condition:
                break
            
            # Execute block
            interpreter = EddieInterpreter()
            interpreter.variables = self.variables
            interpreter.parse(block_tokens)
            self.variables = interpreter.variables
    
    def parse_repeat_statement(self) -> None:
        """Parse: repeat (count) { ... }"""
        if not self.expect('repeat'):
            raise SyntaxError("Expected 'repeat'")
        
        if not self.expect('('):
            raise SyntaxError("Expected '(' after 'repeat'")
        
        count = int(self.parse_expression())
        
        if not self.expect(')'):
            raise SyntaxError("Expected ')' after repeat count")
        
        if not self.expect('{'):
            raise SyntaxError("Expected '{' to start repeat block")
        
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
        
        block_end = self.token_index
        block_tokens = self.tokens[block_start:block_end]
        
        if not self.expect('}'):
            raise SyntaxError("Expected '}' to close repeat block")
        
        # Execute repeat loop
        for _ in range(count):
            interpreter = EddieInterpreter()
            interpreter.variables = self.variables
            interpreter.parse(block_tokens)
            self.variables = interpreter.variables
    
    def parse_wait_statement(self) -> None:
        """Parse: wait(seconds);"""
        if not self.expect('wait'):
            raise SyntaxError("Expected 'wait'")
        
        if not self.expect('('):
            raise SyntaxError("Expected '(' after 'wait'")
        
        seconds = float(self.parse_expression())
        
        if not self.expect(')'):
            raise SyntaxError("Expected ')' after wait duration")
        
        self.expect(';')
        
        time.sleep(seconds)
    
    def parse_pause_statement(self) -> None:
        """Parse: pause(condition);"""
        if not self.expect('pause'):
            raise SyntaxError("Expected 'pause'")
        
        if not self.expect('('):
            raise SyntaxError("Expected '(' after 'pause'")
        
        condition_start = self.token_index
        condition_tokens = []
        paren_count = 1
        
        while paren_count > 0:
            token = self.current_token()
            if token == '(':
                paren_count += 1
            elif token == ')':
                paren_count -= 1
                if paren_count == 0:
                    break
            condition_tokens.append(token)
            self.advance()
        
        if not self.expect(')'):
            raise SyntaxError("Expected ')' after pause condition")
        
        self.expect(';')
        
        # Wait until condition becomes true
        while True:
            cond_interpreter = EddieInterpreter()
            cond_interpreter.variables = self.variables
            cond_interpreter.tokens = condition_tokens
            cond_interpreter.token_index = 0
            condition = cond_interpreter.parse_expression()
            self.variables = cond_interpreter.variables
            
            if condition:
                break
            time.sleep(0.1)
    
    def parse_ask_statement(self) -> None:
        """Parse: ask("prompt");"""
        if not self.expect('ask'):
            raise SyntaxError("Expected 'ask'")
        
        if not self.expect('('):
            raise SyntaxError("Expected '(' after 'ask'")
        
        prompt = self.parse_expression()
        
        if not self.expect(')'):
            raise SyntaxError("Expected ')' after ask prompt")
        
        self.expect(';')
        
        self.user_input = input(str(prompt))
    
    def parse_timer_statement(self) -> None:
        """Parse: timer();"""
        if not self.expect('timer'):
            raise SyntaxError("Expected 'timer'")
        
        if not self.expect('('):
            raise SyntaxError("Expected '(' after 'timer'")
        
        if not self.expect(')'):
            raise SyntaxError("Expected ')' to close timer()")
        
        self.expect(';')
        
        # Start a timer
        timer_id = f"timer_{len(self.timers)}"
        self.timers[timer_id] = time.time()
        print(f"Timer started: {timer_id}")
    
    def parse_reset_timer_statement(self) -> None:
        """Parse: resetTimer();"""
        if not self.expect('resetTimer'):
            raise SyntaxError("Expected 'resetTimer'")
        
        if not self.expect('('):
            raise SyntaxError("Expected '(' after 'resetTimer'")
        
        if not self.expect(')'):
            raise SyntaxError("Expected ')' to close resetTimer()")
        
        self.expect(';')
        
        # Reset all timers
        if self.timers:
            timer_id = list(self.timers.keys())[-1]
            elapsed = time.time() - self.timers[timer_id]
            print(f"Timer '{timer_id}' elapsed: {elapsed:.2f} seconds")
            del self.timers[timer_id]
        else:
            print("No active timers to reset")
    
    def run_file(self, filename: str) -> None:
        """Run an eddie-lang file."""
        try:
            with open(filename, 'r') as f:
                code = f.read()
            
            tokens = self.tokenize(code)
            self.parse(tokens)
        
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    def run_repl(self) -> None:
        """Run interactive REPL mode."""
        print("Eddie Language REPL")
        print("Type 'exit' to quit")
        print()
        
        while True:
            try:
                line = input("eddie> ").strip()
                
                if line.lower() == 'exit':
                    break
                
                if not line:
                    continue
                
                tokens = self.tokenize(line)
                if tokens:
                    self.parse(tokens)
            
            except KeyboardInterrupt:
                print("\nInterrupted")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main entry point."""
    interpreter = EddieInterpreter()
    
    if len(sys.argv) > 1:
        # File mode
        filename = sys.argv[1]
        interpreter.run_file(filename)
    else:
        # REPL mode
        interpreter.run_repl()


if __name__ == '__main__':
    main()
