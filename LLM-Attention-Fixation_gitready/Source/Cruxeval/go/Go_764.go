package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, old string, new string) string {
	text2 := strings.ReplaceAll(text, old, new)
	old2 := reverseString(old)
	for strings.Contains(text2, old2) {
		text2 = strings.ReplaceAll(text2, old2, new)
	}
	return text2
}

func reverseString(s string) string {
	runes := []rune(s)
	for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
		runes[i], runes[j] = runes[j], runes[i]
	}
	return string(runes)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("some test string", "some", "any"), expected: "any test string" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
