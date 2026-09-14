package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(strs string) string {
	words := strings.Split(strs, " ")
	for i := 1; i < len(words); i += 2 {
		rs := []rune(words[i])
		for i, j := 0, len(rs)-1; i < j; i, j = i+1, j-1 {
			rs[i], rs[j] = rs[j], rs[i]
		}
		words[i] = string(rs)
	}
	return strings.Join(words, " ")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("K zBK"), expected: "K KBz" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
