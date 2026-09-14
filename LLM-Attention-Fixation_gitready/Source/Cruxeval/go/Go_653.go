package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, letter string) int {
	t := text
	for _, alph := range text {
		t = strings.ReplaceAll(t, string(alph), "")
	}

	return len(strings.Split(t, letter))
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("c, c, c ,c, c", "c"), expected: 1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
