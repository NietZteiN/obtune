package main

import (
    "fmt"
    "testing"
    "sort"
)

func f(nums []int) []int {
	sort.Ints(nums)

	n := len(nums)
	newNums := make([]int, 0)

	medianIndex := n / 2
	newNums = append(newNums, nums[medianIndex])

	if n%2 == 0 {
		newNums = append(newNums, nums[medianIndex-1])
	}

	for i := 0; i < n/2; i++ {
		newNums = append([]int{nums[n-i-1]}, newNums...)
		newNums = append(newNums, nums[i])
	}

	return newNums
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1}), expected: []int{1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
