package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, prefix string) string {
	for strings.HasPrefix(text, prefix) {
		text = text[len(prefix):]
		if text == "" {
			break
		}
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
     { actual: candidate("ndbtdabdahesyehu", "n"), expected: "dbtdabdahesyehu" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
