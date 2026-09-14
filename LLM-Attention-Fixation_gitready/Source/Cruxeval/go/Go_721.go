package main

import (
    "fmt"
    "testing"
    "sort"
)

func f(nums []int) []int {
	count := len(nums)
	for num := 2; num < count; num++ {
		sort.Ints(nums)
	}
	return nums
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{-6, -5, -7, -8, 2}), expected: []int{-8, -7, -6, -5, 2} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
