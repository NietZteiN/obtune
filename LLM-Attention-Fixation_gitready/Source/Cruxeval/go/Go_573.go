package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(myString string, prefix string) string {
	if strings.HasPrefix(myString, prefix) {
		return strings.TrimPrefix(myString, prefix)
	}
	return myString
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("Vipra", "via"), expected: "Vipra" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
