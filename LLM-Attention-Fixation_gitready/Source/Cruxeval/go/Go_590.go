package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
	for i := 10; i > 0; i-- {
		text = strings.TrimLeft(text, fmt.Sprintf("%d", i))
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
     { actual: candidate("25000   $"), expected: "5000   $" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
