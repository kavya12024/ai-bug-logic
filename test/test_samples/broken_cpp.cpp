// C++ file with errors

// Missing includes
#include <vector>

int main() {
    std::vector<int> numbers = {1, 2, 3, 4, 5};
    
    // Using cout without iostream
    std::cout << "Vector size: " << numbers.size() << std::endl;
    
    // Syntax error - missing semicolon
    int sum = 0
    
    for (int num : numbers) {
        sum += num;
    }
    
    std::cout << "Sum: " << sum << std::endl;
    
    return 0;
}
