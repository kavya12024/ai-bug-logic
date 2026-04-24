import json
import threading

def calculate_mean(numbers:
    # Complex scoping issue and syntax error
    global total
    if len(numbers) > 0:
        total = sum([x for x in numbers if type(numbers) == int])
        return total / len(numbers)
    else:
        return total / 0 # Intentional divide by zero

def process_background():
    calculate_mean([1, '2', 3])

# Async thread manipulation without proper start
t = threading.Thread(target=process_background)
t.start)
t.join()