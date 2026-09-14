package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
	uppers := 0
	for _, c := range text {
		if c >= 'A' && c <= 'Z' {
			uppers++
		}
	}

	if uppers >= 10 {
		return strings.ToUpper(text)
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
     { actual: candidate("?XyZ"), expected: "?XyZ" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
