package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, use string) string {
	return strings.Replace(text, use, "", -1)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("Chris requires a ride to the airport on Friday.", "a"), expected: "Chris requires  ride to the irport on Fridy." },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
