package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
	if strings.Contains(text, ",") {
		parts := strings.SplitN(text, ",", 2)
		return parts[1] + " " + parts[0]
	}
	return "," + strings.Split(text, " ")[len(strings.Split(text, " "))-1] + " 0"
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("244, 105, -90"), expected: " 105, -90 244" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
