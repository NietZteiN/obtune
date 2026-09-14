package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, length int, index int) string {
	ls := strings.Fields(text)
	if index < len(ls) {
		ls = append(ls[:len(ls)-index], ls[len(ls)-index:]...)
	}
	result := make([]string, 0)
	for _, l := range ls {
		if len(l) >= length {
			result = append(result, l[:length])
		}
	}
	return strings.Join(result, "_")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("hypernimovichyp", 2, 2), expected: "hy" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
