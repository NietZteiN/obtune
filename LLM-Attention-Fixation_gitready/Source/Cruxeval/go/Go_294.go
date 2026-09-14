package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(n string, m string, text string) string {
	if text == "" {
		return text
	}

	head, mid, tail := string(text[0]), text[1:len(text)-1], string(text[len(text)-1])
	joined := strings.ReplaceAll(head, n, m) + strings.ReplaceAll(mid, n, m) + strings.ReplaceAll(tail, n, m)
	return joined
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("x", "$", "2xz&5H3*1a@#a*1hris"), expected: "2$z&5H3*1a@#a*1hris" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
