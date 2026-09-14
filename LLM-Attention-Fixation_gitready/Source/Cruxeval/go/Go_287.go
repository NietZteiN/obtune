package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(name string) string {
	if strings.ToLower(name) == name {
		return strings.ToUpper(name)
	} else {
		return strings.ToLower(name)
	}
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("Pinneaple"), expected: "pinneaple" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
