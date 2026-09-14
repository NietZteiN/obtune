package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, elem string) []string {
	if elem != "" {
		for strings.HasPrefix(text, elem) {
			text = strings.Replace(text, elem, "", 1)
		}
		for strings.HasPrefix(elem, text) {
			elem = strings.Replace(elem, text, "", 1)
		}
	}
	return []string{elem, text}
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("some", "1"), expected: []string{"1", "some"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
