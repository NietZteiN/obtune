package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(s string) string {
	count := len(s) - 1
	reverse_s := reverseString(s)
	for count > 0 && !strings.Contains(reverse_s, "sea") {
		count--
		reverse_s = reverse_s[:count]
	}
	return reverse_s[count:]
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
     { actual: candidate("s a a b s d s a a s a a"), expected: "" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
