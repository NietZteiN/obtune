package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(chars string) string {
	s := ""
	for _, ch := range chars {
		if strings.Count(chars, string(ch))%2 == 0 {
			s += strings.ToUpper(string(ch))
		} else {
			s += string(ch)
		}
	}
	return s
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("acbced"), expected: "aCbCed" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
