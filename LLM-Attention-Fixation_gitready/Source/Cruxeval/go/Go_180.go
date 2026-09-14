package f_test

import (
	"testing"
	"fmt"
)

func f(nums []int) []int {
	a := -1
	var b []int
	if len(nums) > 1 {
		b = nums[1:]
	}
	for len(b) > 0 && a <= b[0] {
		newNums := []int{}
		for _, num := range nums {
			if num != b[0] {
				newNums = append(newNums, num)
			}
		}
		nums = newNums
		a = 0
		b = b[1:]
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
     { actual: candidate([]int{-1, 5, 3, -2, -6, 8, 8}), expected: []int{-1, -2, -6, 8, 8} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
