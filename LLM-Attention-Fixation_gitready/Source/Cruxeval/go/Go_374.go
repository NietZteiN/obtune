package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(seq []string, v string) []string {
	var a []string
	for _, i := range seq {
		if strings.HasSuffix(i, v) {
			a = append(a, i+i)
		}
	}
	return a
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"oH", "ee", "mb", "deft", "n", "zz", "f", "abA"}, "zz"), expected: []string{"zzzz"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
