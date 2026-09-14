package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, delim string) string {
	splitText := strings.Split(text, delim)
	return splitText[1] + delim + splitText[0]
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("bpxa24fc5.", "."), expected: ".bpxa24fc5" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
