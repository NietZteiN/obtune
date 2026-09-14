package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text1 string, text2 string) int {
	nums := make([]int, len(text2))
	for i := 0; i < len(text2); i++ {
		nums[i] = strings.Count(text1, string(text2[i]))
	}
	total := 0
	for _, num := range nums {
		total += num
	}
	return total
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("jivespdcxc", "sx"), expected: 2 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
