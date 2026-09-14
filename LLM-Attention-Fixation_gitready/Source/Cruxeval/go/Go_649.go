package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, tabsize int) string {
	words := strings.Split(text, "\n")
	var result []string
	for _, word := range words {
		result = append(result, strings.ReplaceAll(word, "\t", strings.Repeat(" ", tabsize)))
	}
	return strings.Join(result, "\n")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("	f9\n	ldf9\n	adf9!\n	f9?", 1), expected: " f9\n ldf9\n adf9!\n f9?" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
