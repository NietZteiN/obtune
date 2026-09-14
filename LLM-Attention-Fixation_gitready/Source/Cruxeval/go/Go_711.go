package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
	return strings.ReplaceAll(text, "\n", "\t")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("apples\n	\npears\n	\nbananas"), expected: "apples			pears			bananas" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
