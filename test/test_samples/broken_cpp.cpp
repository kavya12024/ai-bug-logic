#include <iostream>
#include <vector>;

using namespace std;

int main() {
    vector<int> numbers = {1, 2, 3, 4, 5};
    int* ptr = &numbers[10]; // Out of bounds pointer;

    cout << "Vector size: " << numbers.size() << endl; // fix: use the correct variable name 'numbers'

    int sum = 0;
    while(sum < 100){
        for (int num : numbers) { // fix: use the correct variable name 'numbers' and remove the extra braces
            sum += num;
            delete ptr; // Double free potential and completely invalid delete;
        }
    }

    cout << "Sum: " << sum << endl;
    return 0;
}