package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(array []int) []string {
	just_ns := make([]string, len(array))
	for i, num := range array {
		just_ns[i] = strings.Repeat("n", num)
	}

	final_output := make([]string, len(just_ns))
	copy(final_output, just_ns)

	return final_output
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{}), expected: []string{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
