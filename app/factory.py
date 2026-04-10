from app.operations import add, subtract, multiply, divide
from app.models import OperationType

class CalculationFactory:
    """Factory to compute results based on the operation type using existing operations."""
    
    @staticmethod
    def compute(a: float, b: float, operation: OperationType) -> float:
        if operation == OperationType.ADD:
            return float(add(a, b))
        elif operation == OperationType.SUB:
            return float(subtract(a, b))
        elif operation == OperationType.MULTIPLY:
            return float(multiply(a, b))
        elif operation == OperationType.DIVIDE:
            # The divide function in operations.py already handles ValueError for zero
            return float(divide(a, b))
        else:
            raise ValueError(f"Unsupported operation: {operation}")