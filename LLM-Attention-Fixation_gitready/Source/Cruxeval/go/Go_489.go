package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, value string) string {
	return strings.TrimPrefix(strings.ToLower(text), strings.ToLower(value))
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("coscifysu", "cos"), expected: "cifysu" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
