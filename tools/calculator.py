import core

class CalculatorTool(core.tool.Tool):
    async def calculate(self, expression: str):
        """Evaluates a math expression safely."""
        # allow only math characters
        allowed = set('0123456789+-*/(). ')
        if not all(c in allowed for c in expression):
            raise ValueError("Invalid characters in expression")

        if len(expression) > 100:
            raise ValueError("Expression is too long (max 100 characters)")

        try:
            result = eval(expression, {'__builtins__': {}}, {})
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")

        if not isinstance(result, (int, float)):
            raise ValueError("Result is not a number")

        return result
