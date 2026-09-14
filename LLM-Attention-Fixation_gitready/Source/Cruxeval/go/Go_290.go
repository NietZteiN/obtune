package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, prefix string) string {
	if strings.HasPrefix(text, prefix) {
		return strings.TrimPrefix(text, prefix)
	}
	if strings.Contains(text, prefix) {
		return strings.TrimSpace(strings.ReplaceAll(text, prefix, ""))
	}
	return strings.ToUpper(text)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("abixaaaily", "al"), expected: "ABIXAAAILY" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
