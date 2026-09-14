package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, pre string) string {
	if !strings.HasPrefix(text, pre) {
		return text
	}
	return strings.TrimPrefix(text, pre)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("@hihu@!", "@hihu"), expected: "@!" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
