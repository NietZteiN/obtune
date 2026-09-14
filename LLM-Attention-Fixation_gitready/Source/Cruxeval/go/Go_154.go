package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(s string, c string) string {
	words := strings.Split(s, " ")
	reversed := []string{}
	for i := len(words) - 1; i >= 0; i-- {
		reversed = append(reversed, words[i])
	}
	return c + "  " + strings.Join(reversed, "  ")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("Hello There", "*"), expected: "*  There  Hello" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
