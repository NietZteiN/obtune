package main

import (
    "fmt"
    "strings"
    "strconv"
    "testing"
)

func f(text string) string {
	text = strings.ReplaceAll(text, "#", "1")
	text = strings.ReplaceAll(text, "$", "5")

	if _, err := strconv.Atoi(text); err == nil {
		return "yes"
	} else {
		return "no"
	}
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("A"), expected: "no" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
