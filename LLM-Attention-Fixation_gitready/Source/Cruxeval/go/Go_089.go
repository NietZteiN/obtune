package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(char string) string {
	vowels := "aeiouAEIOU"

	if strings.ContainsAny(vowels, char) {
		if strings.ContainsAny("AEIOU", char) {
			return strings.ToLower(char)
		}
		return strings.ToUpper(char)
	}
	return ""
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("o"), expected: "O" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
