package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
	ls := []rune(text)
	for x := len(ls) - 1; x >= 0; x-- {
		if len(ls) <= 1 {
			break
		}
		if !strings.ContainsRune("zyxwvutsrqponmlkjihgfedcba", ls[x]) {
			ls = append(ls[:x], ls[x+1:]...)
		}
	}
	return string(ls)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("qq"), expected: "qq" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
