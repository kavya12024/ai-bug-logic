#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void process_string(const char* input) {
    char buffer[10];
    strcpy(buffer, input);
    printf("Processed: %s\n", buffer);
}

int main() {
    int *numbers = (int*)malloc(5 * sizeof(int));
    for (int i = 0; i < 5; i++) {
        numbers[i] = 0;
    }
    free(numbers);
    process_string("this_is_a_string_that_will_overflow_the_buffer");
    return 0;
}