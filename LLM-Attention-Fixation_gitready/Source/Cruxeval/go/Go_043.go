package main

import (
    "fmt"
    "testing"
)

func f(n string) int {
	for _, i := range n {
		if i < '0' || i > '9' {
			return -1
		}
	}
	return 0
}

func main() {
	result := f("12345")
	fmt.Println(result) // Output: 0

	result = f("12a45")
	fmt.Println(result) // Output: -1
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("6 ** 2"), expected: -1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
