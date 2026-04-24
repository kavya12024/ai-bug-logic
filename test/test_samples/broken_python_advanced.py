class UserAccount:
    # Mutable default argument will cause all users to share the same history list
    def __init__(self, name, history=[]):
        self.name = name
        self.history = history
        
    def add_transaction(self, amount):
        self.history.append(amount)

def calculate_complex_average(users)
    total = 0
    # Will crash with ZeroDivisionError if history array is empty
    for user in users:
        total += sum(user.history) / len(user.history)
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
