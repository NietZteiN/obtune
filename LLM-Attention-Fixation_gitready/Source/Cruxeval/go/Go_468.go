package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(a string, b string, n int) string {
	result := b
	m := b
	for i := 0; i < n; i++ {
		if m != "" {
			a, m = strings.Replace(a, m, "", 1), ""
			result = m
		}
	}
	return strings.Join(strings.Split(a, b), result)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("unrndqafi", "c", 2), expected: "unrndqafi" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
