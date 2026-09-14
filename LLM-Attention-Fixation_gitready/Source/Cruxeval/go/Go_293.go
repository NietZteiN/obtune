package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
	s := strings.ToLower(text)
	for i := range s {
		if s[i] == 'x' {
			return "no"
		}
	}
	if strings.ToUpper(text) == text {
		return "true"
	}
	return "false"
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("dEXE"), expected: "no" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
