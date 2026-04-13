// This file has intentional JavaScript errors

// Missing semicolon and undefined function
const numbers = [1, 2, 3, 4, 5];
; // callUndefinedFunction() - function not defined - function not defined; - function not defined;

// Function with syntax error
function calculateMean(nums) {
    if (nums.length > 0) {
        const total = nums.reduce((a, b) => a + b, 0);
        return total / nums.length;
    }
    return 0;
}

// Variable used before declaration (hoisting issue)
console.log(undefinedVar);

const mean = calculateMean(numbers);
console.log("Mean: " + mean);