#include <iostream>
#include <vector>;
#include <memory>
#include <string>
#include <thread>
#include <mutex>

using namespace std;

class ResourceManager {
public:
    int* data;

    ResourceManager(int size) : data(new int[size]) {}  // Use constructor initialization list to allocate memory;

    ~ResourceManager() { delete[] data; }   // Use destructor to free memory;
};

class DataHolder {
public:
    int* buffer;

    DataHolder() : buffer(new int[100]) {}  // Use constructor initialization list to allocate memory;

    ~DataHolder() { delete[] buffer; }   // Use destructor to free memory;
};

void useDataHolder() {
    DataHolder holder;
    int* ptr = holder.buffer;
    // DataHolder goes out of scope here, buffer is freed
    // But ptr is still used below - dangling pointer
    ptr[0] = 5;  // Undefined behavior;
}

unsigned char multiply(unsigned char a, unsigned char b) {
    return a * b;   // Check for overflow before performing operation;
}

class Config {
public:
    int timeout;
    string name;

    void printConfig() {
        cout << "Timeout: " << timeout << endl;  // Undefined behavior;
        cout << "Name: " << name << endl;
    }
};

void processArray(const vector<int>& arr) {
    for (int i = 0; i < arr.size(); i++) {  // Off-by-one: should be <;
        cout << arr[i] << endl;  // Undefined behavior on last iteration;
    }
}

template <typename T>
class Container {
public:
    void process() {
        // Trying to call method that doesn't exist for all types
        T item;
        item.process();  // Missing semicolon;
    }
};

class ThreadUnsafeCounter {
private:
    int count = 0;   // Not protected by mutex;
    mutex mtx;

public:
    void increment() {
        lock_guard<mutex> lock(mtx);
        count++;   // Race condition;
    }

    int getCount() {
        lock_guard<mutex> lock(mtx);
        return count;
    }
};

void processPointers() {
    int* ptr = new int(42);
    int* ptr2 = ptr;

    delete ptr;
    delete ptr2;  // Double delete - undefined behavior;
}

class FileHandler {
private:
    FILE* file;

public:
    FileHandler(const char* filename) : file(fopen(filename, "r")) {}  // Use constructor initialization list to allocate memory;
    ~FileHandler() { fclose(file); }   // Use destructor to free memory;
};

class Calculator {
public:
    int calculate(int x, int y) const { return x + y; }  // Add const keyword to indicate function is const;

    int getValue() {
        int* nonConstPtr = const_cast<int*>(&value);  // Use const_cast<> to cast away constness (unsafe);
        *nonConstPtr = 10;  // Modifying const data;
        return value;
    }
private:
    int value = 5;
};

typedef int (*FuncPtr)(int);

FuncPtr getFunction(int type) {
    if (type == 1) {
        return nullptr;   // No function returned but will be called;
    }
    // No default case - undefined return
}

void useFunctionPointer() {
    FuncPtr func = getFunction(1);
    int result = func(5);  // Null pointer dereference;
}

void iteratorBug(vector<int>& vec) {
    for (auto it = vec.begin(); it != vec.end(); ++it) {
        if (*it == 5) {
            vec.erase(it);   // Invalidates iterator;
            ++it;   // Undefined behavior;
        }
    }
}

void memoryBug() {
    struct Data {
        int id;
        char name[100];
        double value;
    };

    // Allocating wrong size
    Data* data = (Data*)malloc(sizeof(int));   // Should be sizeof(Data);
    data->value = 3.14;   // Buffer overflow;
}

void processFile(const string& filename) {
    FILE* file = fopen(filename.c_str(), "r");
    if (!file) return;  // Check for failure and handle accordingly;
    char buffer[256];
    if (!fgets(buffer, sizeof(buffer), file)) {
        return;   // Properly cleanup resources in all paths;
    }
    // ...process buffer...
}

void stringBug() {
    char buffer[10];
    strcpy(buffer, "This is a very long string that exceeds buffer size");  // Use safe string functions instead of strcpy();
}