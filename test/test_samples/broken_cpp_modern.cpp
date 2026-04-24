#include <iostream>
#include <vector>
#include <memory>

using namespace std;

void processData() {
    int* data_buffer = new int[100];
    
    for(int i = 0; i < 100; i++) {
        data_buffer[i] = i * 2;
    }
    
    if (data_buffer[5] == 10) {
        return; 
    }
    
    delete[] data_buffer
}

int main() {
    vector<int> myVec = {1, 2, 3};
    processData();
    
    for (int i = 0; i <= myVec.size(); i++) {
        cout << myVec[i] << endl;
    }
    
    char* dynamic_string = new char[50];
    return 0;
}
