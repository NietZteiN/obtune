package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(s1 string, s2 string) []int {
	var res []int
	i := strings.LastIndex(s1, s2)
	for i != -1 {
		res = append(res, i+len(s2)-1)
		i = strings.LastIndex(s1[:i], s2)
	}
	return res
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("abcdefghabc", "abc"), expected: []int{10, 2} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
