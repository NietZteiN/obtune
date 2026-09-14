package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(sample string) int {
	i := -1
	for {
		nextIndex := strings.Index(sample[i+1:], "/")
		if nextIndex == -1 {
			break
		}
		i = nextIndex + i + 1
	}
	return strings.LastIndex(sample[:i], "/")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("present/here/car%2Fwe"), expected: 7 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
