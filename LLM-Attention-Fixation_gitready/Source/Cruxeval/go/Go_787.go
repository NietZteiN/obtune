package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
    if len(text) == 0 {
        return ""
    }
    text = strings.ToLower(text)
    return strings.ToUpper(string(text[0])) + text[1:]
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("xzd"), expected: "Xzd" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
