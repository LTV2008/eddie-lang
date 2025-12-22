import sys
import re
import math
import random
import time
from typing import Any, List, Dict


# ----------------------------------------------------------------------
# Custom Exceptions
# ----------------------------------------------------------------------
class InterpreterError(Exception):
    """Raised for any runtime / syntax error inside the interpreter."""
    def __init__(self, message: str, line_number: int = None, column_number: int = None):
        super().__init__(message)
        self.line_number = line_number
        self.column_number = column_number

    def __str__(self) -> str:
        loc = ""
        if self.line_number is not None:
            loc += f"Line {self.line_number}"
        if self.column_number is not None:
            loc += f", Column {self.column_number}"
        return f"{loc}: {super().__str__()}"


class ReturnSignal(Exception):
    """Used internally to unwind the call‑stack when a function returns."""
    def __init__(self, value: Any = None):
        self.value = value


# ----------------------------------------------------------------------
# Interpreter Core
# ----------------------------------------------------------------------
class Interpreter:
    # ------------------------------------------------------------------
    # Construction / state
    # ------------------------------------------------------------------
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, Dict] = {}
        self.const_variables: set = set()
        self._scope_stack: List[Dict[str, Any]] = []   # for proper lexical scoping

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def run(self, code: str, interactive: bool = False) -> Any:
        """Execute a block of source code."""
        lines = code.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            try:
                # ---------------------------------------------------------
                # 1️⃣  Skip blanks / comments
                # ---------------------------------------------------------
                if not line or line.startswith("//") or line.startswith("/*"):
                    i += 1
                    continue

                # ---------------------------------------------------------
                # 2️⃣  Dispatch based on the first token
                # ---------------------------------------------------------
                if line.startswith("println"):
                    self._execute_println(line, i + 1)
                elif line.startswith("print"):
                    self._execute_print(line, i + 1)
                elif re.match(r"var|let|const", line):
                    self._execute_variable_declaration(line, i + 1)
                elif line.startswith("function "):
                    i = self._execute_function_definition(lines, i)
                    continue
                elif line.startswith("return "):
                    self._execute_return(line, i + 1)
                elif line.startswith("if"):
                    i = self._execute_if_block(lines, i)
                    continue
                elif line.startswith("for"):
                    i = self._execute_for_loop(lines, i)
                    continue
                elif line.startswith("while"):
                    i = self._execute_while_loop(lines, i)
                    continue
                elif line.startswith("repeat"):
                    i = self._execute_repeat_loop(lines, i)
                    continue
                elif line.startswith("wait") or line.startswith("sleep"):
                    self._execute_wait(line, i + 1)
                elif "=" in line and not line.startswith("=="):
                    self._execute_assignment(line, i + 1)
                else:
                    # Anything that isn’t a statement is treated as an expression
                    self._evaluate_expression(line, i + 1)

                i += 1

            except ReturnSignal as ret:
                return ret.value
            except InterpreterError as e:
                if interactive:
                    print(f"Error: {e}")
                    i += 1
                else:
                    raise
            except Exception as e:
                raise InterpreterError(str(e), line_number=i + 1)

    # ------------------------------------------------------------------
    # 1️⃣  Print helpers
    # ------------------------------------------------------------------
    def _execute_println(self, line: str, line_number: int) -> None:
        match = re.match(r"println\((.*)\)", line)
        if not match:
            raise InterpreterError("Syntax error in println statement", line_number)
        expr = match.group(1)
        value = self._evaluate_expression(expr, line_number)
        print(value)

    def _execute_print(self, line: str, line_number: int) -> None:
        match = re.match(r"print\((.*)\)", line)
        if not match:
            raise InterpreterError("Syntax error in print statement", line_number)
        expr = match.group(1)
        value = self._evaluate_expression(expr, line_number)
        print(value, end="")

    # ------------------------------------------------------------------
    # 2️⃣  Variable handling
    # ------------------------------------------------------------------
    def _execute_variable_declaration(self, line: str, line_number: int) -> None:
        """var / let / const declarations."""
        match = re.match(r"(var|let|const)\s+(\w+)(?:\s*=\s*(.*))?", line)
        if not match:
            raise InterpreterError("Syntax error in variable declaration", line_number)

        decl_type, name, init_expr = match.groups()
        if name in self.variables:
            raise InterpreterError(f"Variable '{name}' already declared", line_number)

        if decl_type == "const" and init_expr is None:
            raise InterpreterError("Const variables must be initialized", line_number)

        value = self._evaluate_expression(init_expr, line_number) if init_expr else None
        self.variables[name] = value
        if decl_type == "const":
            self.const_variables.add(name)

    def _execute_assignment(self, line: str, line_number: int) -> None:
        """Simple assignment (no `var`/`let`)."""
        match = re.match(r"(\w+)\s*=\s*(.*)", line)
        if not match:
            raise InterpreterError("Syntax error in assignment", line_number)

        name, expr = match.groups()
        if name not in self.variables:
            raise InterpreterError(f"Variable '{name}' not declared", line_number)
        if name in self.const_variables:
            raise InterpreterError(f"Cannot reassign constant '{name}'", line_number)

        self.variables[name] = self._evaluate_expression(expr, line_number)

    # ------------------------------------------------------------------
    # 3️⃣  Function handling
    # ------------------------------------------------------------------
    def _execute_function_definition(self, lines: List[str], start_idx: int) -> int:
        header = lines[start_idx].strip()
        match = re.match(r"function\s+(\w+)\s*\((.*?)\)\s*{", header)
        if not match:
            raise InterpreterError("Syntax error in function definition", start_idx + 1)

        name, param_str = match.groups()
        params = [p.strip() for p in param_str.split(",") if p.strip()]

        body = []
        i = start_idx + 1
        while i < len(lines):
            cur = lines[i].strip()
            if cur == "}":
                break
            body.append(cur)
            i += 1
        else:
            raise InterpreterError(f"Missing closing '}}' for function '{name}'", start_idx + 1)

        self.functions[name] = {"params": params, "body": body}
        return i  # index of the closing brace

    def _invoke_function(self, name: str, args: List[Any], line_number: int) -> Any:
        func = self.functions.get(name)
        if not func:
            raise InterpreterError(f"Function '{name}' not defined", line_number)

        if len(args) != len(func["params"]):
            raise InterpreterError(
                f"Function '{name}' expects {len(func['params'])} args, got {len(args)}",
                line_number,
            )

        # ----- lexical scope handling -----
        # push current scope, replace with a new one containing parameters
        self._scope_stack.append(self.variables)
        local_scope = dict(zip(func["params"], args))
        self.variables = local_scope

        try:
            self.run("\n".join(func["body"]))
        except ReturnSignal as ret:
            return ret.value
        finally:
            # restore previous scope
            self.variables = self._scope_stack.pop()
        return None

    def _execute_return(self, line: str, line_number: int) -> None:
        match = re.match(r"return\s+(.*)", line)
        if not match:
            raise InterpreterError("Syntax error in return statement", line_number)
        expr = match.group(1)
        value = self._evaluate_expression(expr, line_number)
        raise ReturnSignal(value)

    # ------------------------------------------------------------------
    # 4️⃣  Control structures
    # ------------------------------------------------------------------
    def _execute_if_block(self, lines: List[str], start_idx: int) -> int:
        """Handles if / else if / else chains."""
        i = start_idx
        executed = False

        while i < len(lines):
            line = lines[i].strip()
            # ---- if / else if ----
            if line.startswith("if") or line.startswith("else if"):
                cond_match = re.match(r"(if|else if)\s*\((.*)\
