package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, char string) string {
	charIndex := strings.Index(text, char)
	var result []rune
	if charIndex > 0 {
		result = []rune(text[:charIndex])
	}
	result = append(result, []rune(char)...)
	result = append(result, []rune(text[charIndex+len(char):])...)
	return string(result)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("llomnrpc", "x"), expected: "xllomnrpc" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
