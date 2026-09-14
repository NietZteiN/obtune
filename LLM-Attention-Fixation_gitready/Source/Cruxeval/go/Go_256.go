package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, sub string) int {
	a := 0
	b := len(text) - 1

	for a <= b {
		c := (a + b) / 2
		if lastIndex := strings.LastIndex(text, sub); lastIndex >= c {
			a = c + 1
		} else {
			b = c - 1
		}
	}

	return a
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("dorfunctions", "2"), expected: 0 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
