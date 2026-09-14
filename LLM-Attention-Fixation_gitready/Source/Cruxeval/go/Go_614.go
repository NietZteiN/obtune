package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, substr string, occ int) int {
	n := 0
	for {
		i := strings.LastIndex(text, substr)
		if i == -1 {
			break
		} else if n == occ {
			return i
		} else {
			n++
			text = text[:i]
		}
	}
	return -1
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("zjegiymjc", "j", 2), expected: -1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
