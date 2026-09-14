package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, pref string) bool {
	if pref == "" {
		return false
	}
	if pref[0] == '[' {
		// Split the comma separated values in pref
		// and check if any of the values is a prefix of text
		return false // Replace this with the appropriate logic
	}
	return strings.HasPrefix(text, pref)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("Hello World", "W"), expected: false },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
