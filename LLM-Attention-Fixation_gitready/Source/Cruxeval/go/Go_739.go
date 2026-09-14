package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(st string, pattern []string) bool {
	for _, p := range pattern {
		if !strings.HasPrefix(st, p) {
			return false
		}
		st = strings.TrimPrefix(st, p)
	}
	return true
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("qwbnjrxs", []string{"jr", "b", "r", "qw"}), expected: false },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
