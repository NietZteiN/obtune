package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, char string, min_count int) string {
	count := strings.Count(text, char)
	if count < min_count {
		return strings.ToUpper(text)
	}
	return text
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("wwwwhhhtttpp", "w", 3), expected: "wwwwhhhtttpp" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
