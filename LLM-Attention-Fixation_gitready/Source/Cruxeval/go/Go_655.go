package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(s string) string {
	s = strings.ReplaceAll(s, "a", "")
	s = strings.ReplaceAll(s, "r", "")
	return s
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("rpaar"), expected: "p" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
