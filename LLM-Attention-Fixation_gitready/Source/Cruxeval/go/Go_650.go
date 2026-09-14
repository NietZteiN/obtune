package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(myString string, substring string) string {
	for strings.HasPrefix(myString, substring) {
		myString = myString[len(substring):len(myString)]
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
     { actual: candidate("", "A"), expected: "" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
