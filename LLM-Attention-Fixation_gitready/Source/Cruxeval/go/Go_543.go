package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(item string) string {
	modified := strings.ReplaceAll(strings.ReplaceAll(strings.ReplaceAll(strings.ReplaceAll(item, ". ", " , "), "&#33; ", "! "), ". ", "? "), ". ", ". ")
	firstLetter := strings.ToUpper(string(modified[0]))
	modified = firstLetter + modified[1:]
	return modified
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(".,,,,,. منبت"), expected: ".,,,,, , منبت" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
