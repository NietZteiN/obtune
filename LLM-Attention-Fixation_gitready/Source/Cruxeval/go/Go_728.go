package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
	result := ""
	for i, ch := range text {
		if ch == []rune(text)[i] {
			continue
		}
		if len(text)-1-i < strings.LastIndex(text, strings.ToLower(string(ch))) {
			result += string(ch)
		}
	}
	return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("ru"), expected: "" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
