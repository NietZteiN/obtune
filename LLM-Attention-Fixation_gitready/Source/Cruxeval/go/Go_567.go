package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(s string, n int) []string {
	ls := strings.Split(s, " ")
	out := []string{}
	for len(ls) >= n {
		out = append(out, ls[len(ls)-n:len(ls)]...)
		ls = ls[:len(ls)-n]
	}
	outStr := strings.Join(out, "_")
	return append(ls, outStr)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("one two three four five", 3), expected: []string{"one", "two", "three_four_five"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
