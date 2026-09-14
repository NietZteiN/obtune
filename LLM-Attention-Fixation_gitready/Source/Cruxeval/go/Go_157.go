package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(phrase string) int {
	ans := 0
	words := strings.Fields(phrase)
	for _, word := range words {
		for _, ch := range word {
			if string(ch) == "0" {
				ans++
			}
		}
	}
	return ans
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("aboba 212 has 0 digits"), expected: 1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
