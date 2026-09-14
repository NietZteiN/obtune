package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
    text = strings.ToLower(text)
    head, tail := text[0], text[1:]
    return strings.ToUpper(string(head)) + tail
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("Manolo"), expected: "Manolo" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
