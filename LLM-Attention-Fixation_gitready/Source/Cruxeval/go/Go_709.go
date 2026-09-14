package main

import (
    "fmt"
    "strings"
    "testing"
    "sort"
)

func f(text string) string {
	words := strings.Split(text, " ")
	sort.Sort(sort.Reverse(sort.StringSlice(words)))
	return strings.Join(words, " ")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("a loved"), expected: "loved a" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
