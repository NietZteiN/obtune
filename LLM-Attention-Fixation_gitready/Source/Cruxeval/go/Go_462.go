package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, value string) string {
	length := len(text)
	letters := []rune(text)
	if strings.IndexRune(text, rune(value[0])) == -1 {
		value = string(letters[0])
	}
	return strings.Repeat(value, length)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("ldebgp o", "o"), expected: "oooooooo" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
