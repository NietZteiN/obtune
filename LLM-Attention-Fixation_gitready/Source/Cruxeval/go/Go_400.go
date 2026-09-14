package main

import (
    "unicode/utf8"
    "fmt"
    "strings"
    "testing"
)

func f(multi_string string) string {
	words := strings.Fields(multi_string)
	var asciiWords []string
	for _, word := range words {
		if utf8.ValidString(word) {
			asciiWords = append(asciiWords, word)
		}
	}
	return strings.Join(asciiWords, ", ")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("I am hungry! eat food."), expected: "I, am, hungry!, eat, food." },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
