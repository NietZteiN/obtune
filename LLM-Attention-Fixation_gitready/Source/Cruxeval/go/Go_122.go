package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(myString string) string {
	if myString[:4] != "Nuva" {
		return "no"
	} else {
		return strings.TrimSpace(myString)
	}
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("Nuva?dlfuyjys"), expected: "Nuva?dlfuyjys" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
