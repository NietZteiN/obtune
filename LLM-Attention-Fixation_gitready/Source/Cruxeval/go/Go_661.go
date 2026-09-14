package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(letters string, maxsplit int) string {
	words := strings.Fields(letters)
	startIndex := len(words) - maxsplit
	if startIndex < 0 {
		startIndex = 0
	}
	return strings.Join(words[startIndex:], "")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("elrts,SS ee", 6), expected: "elrts,SSee" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
