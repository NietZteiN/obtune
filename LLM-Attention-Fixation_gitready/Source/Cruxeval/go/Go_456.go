package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(s string, tab int) string {
	return strings.ReplaceAll(s, "\t", strings.Repeat(" ", tab))
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("Join us in Hungary", 4), expected: "Join us in Hungary" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
