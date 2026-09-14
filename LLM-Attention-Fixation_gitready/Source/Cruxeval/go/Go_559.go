package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(n string) string {
	n = string(n)
	return string(n[0]) + "." + strings.ReplaceAll(string(n[1:]), "-", "_")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("first-second-third"), expected: "f.irst_second_third" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
