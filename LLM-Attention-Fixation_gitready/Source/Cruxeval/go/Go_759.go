package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, sub string) []int {
	var index []int
	starting := 0
	for starting != -1 {
		starting = strings.Index(text[starting:], sub)
		if starting != -1 {
			index = append(index, starting)
			starting += len(sub)
		}
	}
	return index
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("egmdartoa", "good"), expected: []int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
