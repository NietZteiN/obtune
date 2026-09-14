package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(s string) int {
	c := ""
	for _, i := range s {
		c = c + string(i)
		if lastIndex := strings.LastIndex(s, c); lastIndex > -1 {
			return lastIndex
		}
	}
	return 0
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("papeluchis"), expected: 2 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
