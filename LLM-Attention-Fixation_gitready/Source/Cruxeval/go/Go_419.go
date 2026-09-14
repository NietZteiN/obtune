package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, value string) string {
	if strings.Contains(text, value) {
		parts := strings.Split(text, value)
		return parts[0]
	}
	return ""
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("mmfbifen", "i"), expected: "mmfb" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
