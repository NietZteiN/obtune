package main

import (
    "fmt"
    "testing"
    "unicode"
)

func f(s string) bool {
	l := []rune(s)
	for i := range l {
		l[i] = unicode.ToLower(l[i])
		if !unicode.IsDigit(l[i]) {
			return false
		}
	}
	return true
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(""), expected: true },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
