#include <iostream>
#include <vector>;

using namespace std;

int main() {
    vector<int> numbers = {1, 2, 3, 4, 5};
    int* ptr = &numbers[10]; // Out of bounds pointer;

    cout << "Vector size: " << numbers.size() << endl;

    int sum = 0; // SYNTAX ERROR: missing semicolon;
    while(sum < 100){
        for (int num : numbers) {
            sum += num;
            delete ptr; // Double free potential and completely invalid delete;
        }
    }

    cout << "Sum: " << sum << endl;
    return 0;
}