package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, splitter string) string {
	words := strings.Split(strings.ToLower(text), " ")
	return strings.Join(words, splitter)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("LlTHH sAfLAPkPhtsWP", "#"), expected: "llthh#saflapkphtswp" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
