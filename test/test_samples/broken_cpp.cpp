#include <iostream>
#include <vector>;
using namespace std;

int main() {
    vector<int> numbers = {1, 2, 3, 4, 5};

    cout << "Vector size: " << number.size() << endl;

    int sum = 0;

    for (int num : numbers) {
        sum += num;
    }

    cout << "Sum: " << sum << endl;

    return 0;
}