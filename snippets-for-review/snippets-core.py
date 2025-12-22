import random
import math


class Interpreter:
    def __init__(self):
        self.variables = {}

    def evaluate(self, expr):
        tokens = expr.split()
        if tokens[0] == "println":
            # Extract content and call print_output
            text = " ".join(tokens[1:]).strip("()\"; ")
            self.print_output(text)
        elif tokens[0].startswith("var ") or tokens[0].startswith("let "):
            # Handle variable declaration
            var_name = tokens[1]
            if "=" in tokens:
                value = eval(" ".join(tokens[3:]).strip(";"))
                self.variables[var_name] = value
        # Further handling for other expressions...


    def print_output(self, *args):
        print(" ".join(map(str, args)))

    def read_input(self, prompt):
        return input(prompt)

    def parse(self, line):
        # Tokenizer and Parser implementation

        # Placeholder to return for demonstration
        return line.strip()

    def run(self, source):
        for line in source:
            line = self.parse(line)
            self.evaluate(line)

    def evaluate(self, expr):
        tokens = expr.split()
        if tokens[0] == "println":
            # Extract content and call print_output
            text = " ".join(tokens[1:]).strip('()"; ')
            self.print_output(text)
        elif tokens[0].startswith("var ") or tokens[0].startswith("let "):
            # Handle variable declaration
            var_name = tokens[1]
            if "=" in tokens:
                value = eval(" ".join(tokens[3:]).strip(";"))
                self.variables[var_name] = value
                # Further handling for other expressions...

    def repl(self):
        print("Welcome to the REPL. Type 'exit' to quit.")
        while True:
            try:
                line = input(">> ")
                if line.lower() == "exit":
                    break
                self.evaluate(self.parse(line))
            except Exception as e:
                print(f"Error: {e}")


def read_from_file(filename):
    with open(filename, "r") as file:
        return file.readlines()


if __name__ == "__main__":
    import sys

    interpreter = Interpreter()

    if len(sys.argv) > 1:
        filename = sys.argv[1]
        source = read_from_file(filename)
    else:
        source = []

    if source:
        interpreter.run(source)
    else:
        interpreter.repl()
