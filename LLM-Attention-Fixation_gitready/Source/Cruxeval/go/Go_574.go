package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(simpons []string) string {
	for len(simpons) > 0 {
		pop := simpons[len(simpons)-1]
		simpons = simpons[:len(simpons)-1]
		if pop == strings.Title(pop) {
			return pop
		}
	}
	return ""
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"George", "Michael", "George", "Costanza"}), expected: "Costanza" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
