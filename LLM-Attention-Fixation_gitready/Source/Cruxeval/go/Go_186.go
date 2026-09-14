package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
	words := strings.Fields(text)
	var strippedWords []string
	for _, word := range words {
		strippedWords = append(strippedWords, strings.TrimLeft(word, " "))
	}
	return strings.Join(strippedWords, " ")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("pvtso"), expected: "pvtso" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
