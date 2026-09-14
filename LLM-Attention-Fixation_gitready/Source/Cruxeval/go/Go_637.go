package main

import (
    "fmt"
    "strings"
    "strconv"
    "testing"
)

func f(text string) string {
	words := strings.Split(text, " ")
	for _, word := range words {
		if _, err := strconv.Atoi(word); err != nil {
			return "no"
		}
	}
	return "yes"
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("03625163633 d"), expected: "no" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
