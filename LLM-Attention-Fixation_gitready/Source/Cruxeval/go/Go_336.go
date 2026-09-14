package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(s string, sep string) string {
	s += sep
	idx := strings.LastIndex(s, sep)
	return s[:idx]
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("234dsfssdfs333324314", "s"), expected: "234dsfssdfs333324314" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
