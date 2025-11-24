"""
Calculator Code Generation Capability.
"""

from typing import Dict, Any
from datetime import datetime

from ..base_capability import BaseCapability


class CalculatorCapability(BaseCapability):
    """Generate calculator applications."""
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "type": "code_generation",
            "domain": "mathematics",
            "specialty": "basic_arithmetic",
            "language": "python",
            "version": "1.0.0",
            "description": "Generate calculator applications",
        }
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate calculator code."""
        code = '''#!/usr/bin/env python3
"""Simple Calculator"""

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def main():
    print("Calculator")
    print("1. Add")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Divide")
    
    choice = input("Select operation (1-4): ")
    a = float(input("Enter first number: "))
    b = float(input("Enter second number: "))
    
    if choice == "1":
        print(f"Result: {add(a, b)}")
    elif choice == "2":
        print(f"Result: {subtract(a, b)}")
    elif choice == "3":
        print(f"Result: {multiply(a, b)}")
    elif choice == "4":
        print(f"Result: {divide(a, b)}")

if __name__ == "__main__":
    main()
'''
        
        return {
            "content": code,
            "metadata": {
                "generator": "CalculatorCapability",
                "generated_at": datetime.now().isoformat(),
            },
            "artifacts": [
                {
                    "filename": "calculator.py",
                    "content": code,
                    "type": "python",
                    "executable": True,
                }
            ]
        }