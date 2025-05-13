from smolagents.tools import Tool

class Calculator(Tool):
    name = "calculator"
    description = "Performs basic arithmetic operations: add, subtract, multiply, divide."
    inputs = {
        "a": {
            "type": "number",
            "description": "The first number in the arithmetic operation."
        },
        "b": {
            "type": "number",
            "description": "The second number in the arithmetic operation."
        },
        "op": {
            "type": "string",
            "description": "The operation to perform: 'add', 'subtract', 'multiply', or 'divide'."
        }
    }
    output_type = "string"

    def forward(self, a: float, b: float, op: str) -> str:
        if op == "add":
            return a + b
        elif op == "subtract":
            return a - b
        elif op == "multiply":
            return a * b
        elif op == "divide":
            return a / b if b != 0 else None
        else:
            return "Failed to calculate the result. Please check the operation."