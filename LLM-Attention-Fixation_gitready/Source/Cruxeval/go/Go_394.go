package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) int {
	k := strings.Split(text, "\n")
	i := 0

	for _, j := range k {
		if len(j) == 0 {
			return i
		}
		i++
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
     { actual: candidate("2 m2 \n\nbike"), expected: 1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
