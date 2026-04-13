import json

def calculate_mean(numbers):
    if len(numbers) > 0:
        total = sum(numbers)
        return total / len(numbers)
    else:
        return 0

result = calculate_mean([1, 2, 3, 4])
print(result)