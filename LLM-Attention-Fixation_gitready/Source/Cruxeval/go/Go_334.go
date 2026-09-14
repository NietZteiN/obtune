package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(a string, b []string) string {
	return strings.Join(b, a)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("00", []string{"nU", " 9 rCSAz", "w", " lpA5BO", "sizL", "i7rlVr"}), expected: "nU00 9 rCSAz00w00 lpA5BO00sizL00i7rlVr" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
