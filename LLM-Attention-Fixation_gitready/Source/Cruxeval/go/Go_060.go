package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(doc string) string {
	for _, x := range doc {
		if x >= 'a' && x <= 'z' || x >= 'A' && x <= 'Z' {
			return strings.ToUpper(string(x))
		}
	}
	return "-"
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("raruwa"), expected: "R" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
