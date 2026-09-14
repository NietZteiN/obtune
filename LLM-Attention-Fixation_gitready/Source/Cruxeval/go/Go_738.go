package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, characters string) string {
	for i := range characters {
		text = strings.TrimRight(text, string(characters[i]))
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
     { actual: candidate("r;r;r;r;r;r;r;r;r", "x.r"), expected: "r;r;r;r;r;r;r;r;" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
