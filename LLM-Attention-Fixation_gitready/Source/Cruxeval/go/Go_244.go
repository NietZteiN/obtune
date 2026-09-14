package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, symbols string) string {
	count := 0
	if symbols != "" {
		for range symbols {
			count++
		}
		text = strings.Repeat(text, count)
	}
	return text + strings.Repeat(" ", len(text) + count*2 - 2)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("", "BC1ty"), expected: "        " },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
