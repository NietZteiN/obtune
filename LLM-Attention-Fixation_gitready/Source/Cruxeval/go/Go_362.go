package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
	for i := 0; i < len(text)-1; i++ {
		if text[i:] == strings.ToLower(text[i:]) {
			return text[i+1:]
		}
	}
	return ""
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("wrazugizoernmgzu"), expected: "razugizoernmgzu" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
