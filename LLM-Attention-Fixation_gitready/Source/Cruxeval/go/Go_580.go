package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, char string) []int {
	var new_text string = text
	var a []int

	for {
		index := strings.Index(new_text, char)
		if index == -1 {
			break
		}
		a = append(a, index)
		new_text = strings.Replace(new_text, char, "", 1)
	}

	return a
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("rvr", "r"), expected: []int{0, 1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
