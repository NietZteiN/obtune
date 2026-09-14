package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(strands []string) string {
	subs := strands
	for i, j := range subs {
		for k := 0; k < len(j)/2; k++ {
			subs[i] = string(j[len(j)-1]) + j[1:len(j)-1] + string(j[0])
		}
	}
	return strings.Join(subs, "")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"__", "1", ".", "0", "r0", "__", "a_j", "6", "__", "6"}), expected: "__1.00r__j_a6__6" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
