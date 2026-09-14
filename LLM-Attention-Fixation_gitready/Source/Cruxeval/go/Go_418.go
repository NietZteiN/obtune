package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(s string, p string) string {
	arr := strings.SplitN(s, p, 2)
	if len(arr) == 3 && len(arr[0]) >= 2 && len(arr[1]) <= 2 && len(arr[2]) >= 2 {
		return reverseString(arr[0]) + arr[1] + reverseString(arr[2]) + "#"
	}
	return s
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
     { actual: candidate("qqqqq", "qqq"), expected: "qqqqq" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
