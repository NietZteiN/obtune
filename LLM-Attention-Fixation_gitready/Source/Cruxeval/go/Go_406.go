package main

import (
    "fmt"
    "strings"
    "testing"
    "unicode"
)

func f(text string) bool {
	ls := []rune(text)
	ls[0], ls[len(ls)-1] = unicode.ToUpper(ls[len(ls)-1]), unicode.ToUpper(ls[0])
	return strings.Title(string(ls)) == text
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("Josh"), expected: false },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
