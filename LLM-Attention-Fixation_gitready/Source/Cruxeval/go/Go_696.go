package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) int {
	s := 0
	for i := 1; i < len(text); i++ {
		s += len(text[:strings.LastIndex(text, string(text[i]))])
	}
	return s
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("wdj"), expected: 3 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
