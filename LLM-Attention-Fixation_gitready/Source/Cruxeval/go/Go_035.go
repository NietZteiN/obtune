package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(pattern string, items []string) []int {
	var result []int

	for _, text := range items {
		pos := strings.LastIndex(text, pattern)
		if pos >= 0 {
			result = append(result, pos)
		}
	}

	return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(" B ", []string{" bBb ", " BaB ", " bB", " bBbB ", " bbb"}), expected: []int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
