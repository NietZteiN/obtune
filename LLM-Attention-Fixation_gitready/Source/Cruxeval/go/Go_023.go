package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, chars string) string {
	if chars != "" {
		text = strings.TrimRight(text, chars)
	} else {
		text = strings.TrimRight(text, " ")
	}

	if text == "" {
		return "-"
	}
	return text
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("new-medium-performing-application - XQuery 2.2", "0123456789-"), expected: "new-medium-performing-application - XQuery 2." },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
