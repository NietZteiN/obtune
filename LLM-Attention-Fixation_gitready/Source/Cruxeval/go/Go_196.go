package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
	text = strings.Replace(text, " x", " x.", -1)
	if strings.Title(text) == text {
		return "correct"
	}
	text = strings.Replace(text, " x.", " x", -1)
	return "mixed"
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("398 Is A Poor Year To Sow"), expected: "correct" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
