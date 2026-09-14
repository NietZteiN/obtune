package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(s string, char string) string {
	count := strings.Count(s, char)
	base := strings.Repeat(char, count+1)
	return strings.TrimSuffix(s, base)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("mnmnj krupa...##!@#!@#$$@##", "@"), expected: "mnmnj krupa...##!@#!@#$$@##" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
