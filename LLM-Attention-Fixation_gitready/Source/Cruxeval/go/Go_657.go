package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
	for _, punct := range "!.?,:;" {
		if strings.Count(text, string(punct)) > 1 {
			return "no"
		}
		if strings.HasSuffix(text, string(punct)) {
			return "no"
		}
	}

	return strings.Title(text)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("djhasghasgdha"), expected: "Djhasghasgdha" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
