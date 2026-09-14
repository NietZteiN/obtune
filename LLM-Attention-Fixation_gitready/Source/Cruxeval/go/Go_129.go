package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, search_string string) []int {
	var indexes []int
	for {
		index := strings.LastIndex(text, search_string)
		if index == -1 {
			break
		}
		indexes = append(indexes, index)
		text = text[:index]
	}
	return indexes
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("ONBPICJOHRHDJOSNCPNJ9ONTHBQCJ", "J"), expected: []int{28, 19, 12, 6} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
