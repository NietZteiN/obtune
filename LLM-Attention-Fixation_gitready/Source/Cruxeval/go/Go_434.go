package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(myString string) int {
	index := strings.LastIndex(myString, "e")
	if index != -1 {
		return index
	} else {
		return -1 // Return -1 for the case when 'e' is not found
	}
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("eeuseeeoehasa"), expected: 8 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
