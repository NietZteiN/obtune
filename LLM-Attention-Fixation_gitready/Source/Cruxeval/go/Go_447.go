package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, tab_size int) string {
	res := ""
	text = strings.ReplaceAll(text, "\t", strings.Repeat(" ", tab_size-1))
	for i := 0; i < len(text); i++ {
		if text[i] == ' ' {
			res += "|"
		} else {
			res += string(text[i])
		}
	}
	return res
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("	a", 3), expected: "||a" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
