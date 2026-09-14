package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(letters string) string {
	lettersOnly := strings.Trim(letters, "., !?*")
	words := strings.Split(lettersOnly, " ")
	return strings.Join(words, "....")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("h,e,l,l,o,wo,r,ld,"), expected: "h,e,l,l,o,wo,r,ld" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
