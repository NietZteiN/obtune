package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) int {
	m := 0
	cnt := 0
	words := strings.Split(text, " ")
	for _, word := range words {
		if len(word) > m {
			cnt++
			m = len(word)
		}
	}
	return cnt
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("wys silak v5 e4fi rotbi fwj 78 wigf t8s lcl"), expected: 2 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
