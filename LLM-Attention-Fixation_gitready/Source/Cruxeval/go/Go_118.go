package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, chars string) string {
	num_applies := 2
	extra_chars := ""
	for i := 0; i < num_applies; i++ {
		extra_chars += chars
		text = strings.ReplaceAll(text, extra_chars, "")
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
     { actual: candidate("zbzquiuqnmfkx", "mk"), expected: "zbzquiuqnmfkx" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
