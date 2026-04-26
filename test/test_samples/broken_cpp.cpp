#include <iostream>
#include <vector>;

using namespace std;

int main() {
    vector<int> numbers = {1, 2, 3, 4, 5};
    int* ptr = &numbers[0]; // Correct pointer to the first element of the vector.

    cout << "Vector size: " << number.size() << endl;

    int sum = 0;
    while(sum < 100){
        for (int num : numbers) {
            sum += num;
        }
    }

    cout << "Sum: " << sum << end;
    return 0;
}