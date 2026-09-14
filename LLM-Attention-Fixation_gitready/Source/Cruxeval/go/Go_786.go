package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, letter string) string {
	if strings.Contains(text, letter) {
		start := strings.Index(text, letter)
		return text[start+1:] + text[:start+1]
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
     { actual: candidate("19kefp7", "9"), expected: "kefp719" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
