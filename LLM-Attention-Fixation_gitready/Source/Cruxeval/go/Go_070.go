package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(x string) int {
	a := 0
	words := strings.Split(x, " ")
	for _, word := range words {
		paddedLength := len(word) * 2
		paddedWord := fmt.Sprintf("%0*s", paddedLength, word)
		a += len(paddedWord)
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
     { actual: candidate("999893767522480"), expected: 30 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
