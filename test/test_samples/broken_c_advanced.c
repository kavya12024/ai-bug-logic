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
    int uninitialized_value;
    if (uninitialized_value == 5) {
        printf("Value is 5\n");
    }
    free(numbers);
    //free(numbers); <-- remove duplicate call to free()
    process_string("this_is_a_string_that_will_overflow_the_buffer");
    return 0;
}