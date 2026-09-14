package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) int {
	splitText := strings.Split(text, ",")
	stringA := splitText[0]
	stringB := splitText[1]
	return -(len(stringA) + len(stringB))
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("dog,cat"), expected: -6 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
