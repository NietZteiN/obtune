package main

import (
    "fmt"
    "strings"
    "testing"
)

func partition(text string, value string) (string, string, string) {
	index := strings.Index(text, value)
	if index == -1 {
		return text, "", ""
	}
	return text[:index], value, text[index+len(value):]
}

func f(text string, value string) string {
	left, _, right := partition(text, value)
	return right + left
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("difkj rinpx", "k"), expected: "j rinpxdif" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
