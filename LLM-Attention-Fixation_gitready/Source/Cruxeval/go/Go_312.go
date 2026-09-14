package main

import (
    "fmt"
    "testing"
    "unicode"
)

func isAlnum(s string) bool {
	for _, r := range s {
		if !unicode.IsLetter(r) && !unicode.IsNumber(r) {
			return false
		}
	}
	return true
}

func f(s string) string {
	if isAlnum(s) {
		return "True"
	}
	return "False"
}

func main() {
	fmt.Println(f("abc123")) // Output: True
	fmt.Println(f("abc@123")) // Output: False
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("777"), expected: "True" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
