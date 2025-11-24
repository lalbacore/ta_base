#!/usr/bin/env python3
"""
Simple Calculator Application
Performs basic arithmetic operations.
"""


def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def main():
    """Run the calculator."""
    print("=" * 50)
    print("  Calculator Application")
    print("=" * 50)
    print()
    print("Operations:")
    print("  1. Addition (+)")
    print("  2. Subtraction (-)")
    print("  3. Multiplication (*)")
    print("  4. Division (/)")
    print("  5. Exit")
    print()
    
    while True:
        try:
            choice = input("Select operation (1-5): ").strip()
            
            if choice == '5':
                print("Goodbye!")
                break
            
            if choice not in ['1', '2', '3', '4']:
                print("Invalid choice. Please select 1-5.")
                continue
            
            num1 = float(input("Enter first number: "))
            num2 = float(input("Enter second number: "))
            
            if choice == '1':
                result = add(num1, num2)
                op = "+"
            elif choice == '2':
                result = subtract(num1, num2)
                op = "-"
            elif choice == '3':
                result = multiply(num1, num2)
                op = "*"
            else:
                result = divide(num1, num2)
                op = "/"
            
            print(f"\nResult: {num1} {op} {num2} = {result}\n")
            
        except ValueError as e:
            print(f"Error: {e}\n")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
