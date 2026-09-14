package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) int {
	a := 0
	if len(text) > 0 && strings.Contains(text[1:], string(text[0])) {
		a++
	}
	for i := 0; i < len(text)-1; i++ {
		if strings.Contains(text[i+1:], string(text[i])) {
			a++
		}
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
     { actual: candidate("3eeeeeeoopppppppw14film3oee3"), expected: 18 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
