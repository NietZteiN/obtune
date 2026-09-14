package main

import (
    "fmt"
    "testing"
    "regexp"
)

func f(s string) string {
	if s == "" {
		return "str is empty"
	}
	if match, _ := regexp.MatchString("^[a-zA-Z]+$", s); match {
		return "yes"
	}
	return "no"
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("Boolean"), expected: "yes" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
