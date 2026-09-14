package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(input string) string {
	if isDigit(input) {
		return "int"
	} else if isFloat(input) {
		return "float"
	} else if isString(input) {
		return "str"
	} else if isChar(input) {
		return "char"
	} else {
		return "tuple"
	}
}

func isDigit(input string) bool {
	for _, char := range input {
		if char < '0' || char > '9' {
			return false
		}
	}
	return true
}

func isFloat(input string) bool {
	if strings.Contains(input, ".") {
		parts := strings.Split(input, ".")
		if len(parts) == 2 && isDigit(parts[0]) && isDigit(parts[1]) {
			return true
		}
	}
	return false
}

func isString(input string) bool {
	return strings.Count(input, " ") == len(input)-1
}

func isChar(input string) bool {
	return len(input) == 1
}

func main() {
	fmt.Println(f("123"))      // Output: int
	fmt.Println(f("123.45"))   // Output: float
	fmt.Println(f("hello"))    // Output: str
	fmt.Println(f("a"))        // Output: char
	fmt.Println(f("abc def"))  // Output: tuple
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(" 99 777"), expected: "tuple" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
