package main

import (
    "fmt"
    "strings"
    "testing"
    "unicode"
)

func f(text string) string {
	newText := ""
	for _, ch := range strings.ToLower(strings.TrimSpace(text)) {
		if unicode.IsNumber(ch) || strings.ContainsRune("ÄäÏïÖöÜü", ch) {
			newText += string(ch)
		}
	}
	return newText
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(""), expected: "" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
