package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, suffix string) string {
	if suffix != "" && text != "" && strings.HasSuffix(text, suffix) {
		return strings.TrimSuffix(text, suffix)
	} else {
		return text
	}
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("spider", "ed"), expected: "spider" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
