package main

import (
    "fmt"
    "strings"
    "testing"
)

func isTitle(s string) bool {
	if len(s) == 0 {
		return false
	}
	return strings.ToUpper(s[:1]) == s[:1]
}

func isAlpha(s string) bool {
	for _, char := range s {
		if (char < 'A' || char > 'Z') && (char < 'a' || char > 'z') {
			return false
		}
	}
	return true
}

func f(text string) string {
	if isTitle(text) {
		if len(text) > 1 && strings.ToLower(text) != text {
			return strings.ToLower(string(text[0])) + text[1:]
		}
	} else if isAlpha(text) {
		return strings.Title(text)
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
