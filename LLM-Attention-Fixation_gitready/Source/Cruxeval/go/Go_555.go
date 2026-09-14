package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, tabstop int) string {
	text = strings.ReplaceAll(text, "\n", "_____")
	text = strings.ReplaceAll(text, "\t", strings.Repeat(" ", tabstop))
	text = strings.ReplaceAll(text, "_____", "\n")
	return text
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("odes	code	well", 2), expected: "odes  code  well" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
