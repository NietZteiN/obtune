package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) int {
	vowels := "aeiou"
	maxIndex := -1
	for _, ch := range vowels {
		index := strings.Index(text, string(ch))
		if index > maxIndex {
			maxIndex = index
		}
	}
	return maxIndex
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("qsqgijwmmhbchoj"), expected: 13 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
