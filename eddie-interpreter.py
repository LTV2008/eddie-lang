import sys
import re
import math
import random
import time


class InterpreterError(Exception):
    """Custom error type for interpreter exceptions."""
    def __init__(self, message, line_number=None, column_number=None):
        super().__init__(message)
        self.line_number = line_number
        self.column_number = column_number

    def __str__(self):
        location = ""
        if self.line_number is not None:
            location += f"Line {self.line_number}"
        if self.column_number is not None:
            location += f", Column {self.column_number}"
        return f"{location}: {super().__str__()}"


class ReturnSignal(Exception):
    """Signal for returning a value from a function."""
    def __init__(self, value=None):
        self.value = value


class Interpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}  # Store functions and their definitions
        self.const_variables = set()  # Track `const` variables

    def run(self, code, interactive=False):
        """Executes the provided code line by line."""
        lines = code.split("\n")
        i = 0  # Index for processing lines
        while i < len(lines):
            try:
                line = lines[i].strip()
                if not line or line.startswith("//") or line.startswith("/*"):
                    i += 1
                    continue  # Ignore empty lines and comments

                if line.startswith("println"):
                    self._execute_println(line, i + 1)
                elif line.startswith("print"):
                    self._execute_print(line, i + 1)
                elif re.match(r"var|let|const", line):
                    self._execute_variable_declaration(line, i + 1)
                elif line.startswith("function "):
                    i = self._execute_function_definition(lines, i)
                    continue  # Adjust index as function definition spans multiple lines
                elif "=" in line:
                    self._execute_assignment(line, i + 1)
                elif line.strip() == "}":
                    # Skip closing brace as it is handled in blocks or functions
                    pass
                elif line.startswith("return "):
                    self._execute_return(line, i + 1)
                else:
                    self._evaluate_expression(line, i + 1)
                i += 1
            except ReturnSignal as ret:
                return ret.value
            except InterpreterError as e:
                if interactive:
                    print(f"Error: {e}")
                else:
                    raise
            except Exception as e:
                raise InterpreterError(str(e), line_number=i + 1)

    def _execute_println(self, line, line_number):
        """Handles `println` statements."""
        match = re.match(r"println\((.*)\)", line)
        if not match:
            raise InterpreterError(f"Syntax error in println statement", line_number)
        expr = match.group(1)
        value = self._evaluate_expression(expr, line_number)
        print(value)

    def _execute_print(self, line, line_number):
        """Handles `print` statements."""
        match = re.match(r"print\((.*)\)", line)
        if not match:
            raise InterpreterError(f"Syntax error in print statement", line_number)
        expr = match.group(1)
        value = self._evaluate_expression(expr, line_number)
        print(value, end="")

    def _execute_variable_declaration(self, line, line_number):
        """Handles variable declarations."""
        match = re.match(r"(var|let|const) (\w+)(?: *= *(.*))?", line)
        if not match:
            raise InterpreterError(f"Syntax error in variable declaration", line_number)
        declaration_type, var_name, value_expr = match.groups()
        if var_name in self.variables:
            raise InterpreterError(f"Variable '{var_name}' already declared", line_number)
        value = self._evaluate_expression(value_expr, line_number) if value_expr else None
        self.variables[var_name] = value
        if declaration_type == "const":
            self.const_variables.add(var_name)

    def _execute_assignment(self, line, line_number):
        """Handles assignments to variables."""
        match = re.match(r"(\w+) *= *(.*)", line)
        if not match:
            raise InterpreterError(f"Syntax error in assignment", line_number)
        var_name, value_expr = match.groups()
        if var_name not in self.variables:
            raise InterpreterError(f"Variable '{var_name}' not declared", line_number)
        if var_name in self.const_variables:
            raise InterpreterError(f"Cannot reassign a constant variable '{var_name}'", line_number)
        value = self._evaluate_expression(value_expr, line_number)
        self.variables[var_name] = value

    def _execute_function_definition(self, lines, start_index):
        """Handles multi-line function definitions."""
        first_line = lines[start_index].strip()
        match = re.match(r"function (\w+)\((.*?)\) {", first_line)
        if not match:
            raise InterpreterError(f"Syntax error in function definition", start_index + 1)

        func_name = match.group(1)
        params = [p.strip() for p in match.group(2).split(",") if p.strip()]

        func_body = []
        i = start_index + 1
        while i < len(lines):
            line = lines[i].strip()
            if line == "}":
                break
            func_body.append(line)
            i += 1

        if i >= len(lines):
            raise InterpreterError(f"Missing closing '}}' for function '{func_name}'", start_index + 1)

        self.functions[func_name] = {
            "params": params,
            "body": func_body
        }
        return i  # Return the index of the closing brace

    def _invoke_function(self, func_name, args, line_number):
        """Invokes a function with the specified arguments."""
        func = self.functions.get(func_name)
        if func is None:
            raise InterpreterError(f"Function '{func_name}' is not defined", line_number)

        params = func["params"]
        if len(params) != len(args):
            raise InterpreterError(f"Function '{func_name}' expects {len(params)} arguments but got {len(args)}", line_number)

        # Create a new scope to store local variables
        local_scope = {param: arg for param, arg in zip(params, args)}

        # Backup global variables and replace with local scope temporarily
        global_backup = self.variables.copy()
        self.variables = local_scope

        try:
            # Run the function body
            self.run("\n".join(func["body"]))
        except ReturnSignal as ret:
            self.variables = global_backup  # Restore global variables
            return ret.value
        finally:
            self.variables = global_backup  # Restore global variables
        return None

    def _execute_return(self, line, line_number):
        """Handles `return` statements."""
        match = re.match(r"return (.*)", line)
        if not match:
            raise InterpreterError(f"Syntax error in return statement", line_number)
        value_expr = match.group(1)
        value = self._evaluate_expression(value_expr, line_number)
        raise ReturnSignal(value)

    def _evaluate_expression(self, expr, line_number):
        """Evaluates an expression."""
        if not expr:
            return None
        try:
            # Check for function calls
            match = re.match(r"(\w+)\((.*)\)", expr)
            if match:
                func_name = match.group(1)
                arg_str = match.group(2).strip()  # Extract arguments inside the parentheses

                # Handle empty argument calls (`testScope()`)
                if not arg_str:
                    args = []
                else:
                    # Split and evaluate arguments
                    args = [self._evaluate_expression(arg.strip(), line_number) for arg in arg_str.split(",")]
                return self._invoke_function(func_name, args, line_number)

            # Replace variable names with their values
            expr = re.sub(r"\b(\w+)\b", self._replace_variable, expr)
            return eval(expr, {"__builtins__": None, "math": math, "random": random}, {})
        except KeyError as e:
            raise InterpreterError(f"Variable '{e.args[0]}' is not defined", line_number)
        except Exception as e:
            raise InterpreterError(f"Error evaluating expression '{expr}': {e}", line_number)

    def _replace_variable(self, match):
        """Replaces a variable name in an expression with its value."""
        var_name = match.group(1)
        if var_name in self.variables:
            return str(self.variables[var_name])
        return var_name  # Leave as-is (e.g., function names)

    def repl(self):
        """Starts a Read-Eval-Print Loop (REPL)."""
        print("Eddie REPL. Press ESC or CTRL+C to quit.")
        while True:
            try:
                line = input(">> ")
                if line.lower() in ("^["):
                    break
                self.run(line, interactive=True)
            except (EOFError, KeyboardInterrupt):
                print("\nExiting REPL.")
                break
            except InterpreterError as e:
                print(f"Error: {e}")


def run_file(file_path):
    """Executes the code in a file."""
    interpreter = Interpreter()
    with open(file_path, "r") as file:
        code = file.read()
    try:
        interpreter.run(code)
    except InterpreterError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    interpreter = Interpreter()
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        interpreter.repl()