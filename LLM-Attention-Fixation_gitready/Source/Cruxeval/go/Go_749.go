package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, width int) string {
	result := ""
	lines := strings.Split(text, "\n")
	for _, l := range lines {
		result += strings.Repeat(" ", (width-len(l))/2) + l + strings.Repeat(" ", (width-len(l)+1)/2) + "\n"
	}
	result = result[:len(result)-1]
	return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("l\nl", 2), expected: "l \nl " },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
