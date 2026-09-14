package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, char string) bool {
	if strings.Contains(text, char) {
		textSlice := strings.Split(text, char)
		for i, t := range textSlice {
			textSlice[i] = strings.TrimSpace(t)
		}
		if len(textSlice) > 1 {
			return true
		}
	}
	return false
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("only one line", " "), expected: true },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
