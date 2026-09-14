package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(value string, char string) int {
	total := 0
	for _, c := range value {
		if string(c) == char || string(c) == strings.ToLower(char) {
			total++
		}
	}
	return total
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("234rtccde", "e"), expected: 1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
