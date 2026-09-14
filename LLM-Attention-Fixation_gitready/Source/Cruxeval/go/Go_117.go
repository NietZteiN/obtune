package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(numbers string) int {
	for i := 0; i < len(numbers); i++ {
		if strings.Count(numbers, "3") > 1 {
			return i
		}
	}
	return -1
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("23157"), expected: -1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
