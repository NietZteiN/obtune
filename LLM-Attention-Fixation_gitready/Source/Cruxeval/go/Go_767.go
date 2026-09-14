package main

import (
    "fmt"
    "strings"
    "strconv"
    "testing"
)

func f(text string) string {
	a := strings.Split(strings.TrimSpace(text), " ")
	for i := 0; i < len(a); i++ {
		if _, err := strconv.Atoi(a[i]); err != nil {
			return "-"
		}
	}
	return strings.Join(a, " ")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("d khqw whi fwi bbn 41"), expected: "-" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
