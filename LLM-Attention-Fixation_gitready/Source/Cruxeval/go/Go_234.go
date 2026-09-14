package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, char string) int {
	position := len(text)
	if strings.Contains(text, char) {
		position = strings.Index(text, char)
		if position > 1 {
			position = (position + 1) % len(text)
		}
	}
	return position
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("wduhzxlfk", "w"), expected: 0 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
