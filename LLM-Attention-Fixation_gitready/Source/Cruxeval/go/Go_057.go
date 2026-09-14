package main

import (
    "fmt"
    "strings"
    "testing"
    "unicode"
)

func f(text string) int {
	text = strings.ToUpper(text)
	count_upper := 0
	for _, char := range text {
		if unicode.IsUpper(char) {
			count_upper++
		} else {
			return 0
		}
	}
	return count_upper / 2
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("ax"), expected: 1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
