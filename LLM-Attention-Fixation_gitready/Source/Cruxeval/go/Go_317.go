package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, a string, b string) string {
    text = strings.Replace(text, a, b, -1)
    return strings.Replace(text, b, a, -1)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(" vup a zwwo oihee amuwuuw! ", "a", "u"), expected: " vap a zwwo oihee amawaaw! " },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
