package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
	n := strings.Index(text, "8")
	return strings.Repeat("x0", n)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("sa832d83r xd 8g 26a81xdf"), expected: "x0x0" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
