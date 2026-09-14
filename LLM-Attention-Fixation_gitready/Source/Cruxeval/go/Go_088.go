package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(s1 string, s2 string) string {
	if strings.HasSuffix(s2, s1) {
		s2 = s2[:len(s2)-len(s1)]
	}
	return s2
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("he", "hello"), expected: "hello" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
