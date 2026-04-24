class UserAccount:
    def __init__(self, name, history=[]):
        self.name = name
        self.history = history
    
    def add_transaction(self, amount):
        self.history.append(amount)

def calculate_complex_average(users):
    total = 0
    for user in users:
        try:
            total += sum(user.history) / len(user.history)
        except ZeroDivisionError:
            pass
    return total

if __name__ == '__main__':
    user1 = UserAccount("Alice")
    user2 = UserAccount("Bob")
    user1.add_transaction(100)
    user2.add_transaction(50)
    print(f"Alice history: {user1.history}")
    print(f"Bob history: {user2.history}")
    user3 = UserAccount("Charlie")
    calculate_complex_average([user1, user2, user3])