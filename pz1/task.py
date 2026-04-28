# 1. Програма для знаходження суми двох чисел
def sum_two_numbers():
    try:
        num1 = float(input("Введіть перше число: "))
        num2 = float(input("Введіть друге число: "))
        result = num1 + num2
        print(f"Сума: {result}")
    except ValueError:
        print("Будь ласка, введіть коректні числа.")

### 2. Визначення, чи є число простим
def is_prime(n):
    if n <= 1:
        return False
    
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
            
    return True

# 3. Клас "Калькулятор"
class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Помилка: Ділення на нуль неможливе.")
        return a / b

# Завдання 1
sum_two_numbers()

# Завдання 2
user_input = int(input("Введіть ціле число для перевірки: "))
if is_prime(user_input):
    print(f"Число {user_input} є простим.")
else:
    print(f"Число {user_input} не є простим.")

# Створення екземпляра класу
calc = Calculator()

# Виведення результатів обчислень для певного прикладу
print("=== Результати роботи калькулятора ===")
print(f"Додавання (15 + 5): {calc.add(15, 5)}")
print(f"Віднімання (15 - 5): {calc.subtract(15, 5)}")
print(f"Множення (15 * 5): {calc.multiply(15, 5)}")
print(f"Ділення (15 / 5): {calc.divide(15, 5)}")

# Демонстрація обробки винятку
try:
    print(f"Ділення на нуль: {calc.divide(15, 0)}")
except ValueError as e:
    print(e)
