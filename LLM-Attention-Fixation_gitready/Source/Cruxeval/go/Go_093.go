package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(n string) string {
	length := len(n) + 2
	revn := []rune(n)
	result := string(revn)
	revn = revn[:0]
	return result + strings.Repeat("!", length)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("iq"), expected: "iq!!!!" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
