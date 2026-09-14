package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(value string) string {
	parts := strings.Split(value, " ")
	var result string
	for i := 0; i < len(parts); i += 2 {
		result += parts[i]
	}
	return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("coscifysu"), expected: "coscifysu" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
