package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(prefix string, text string) string {
    if strings.HasPrefix(text, prefix) {
        return text
    } else {
        return prefix + text
    }
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("mjs", "mjqwmjsqjwisojqwiso"), expected: "mjsmjqwmjsqjwisojqwiso" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
