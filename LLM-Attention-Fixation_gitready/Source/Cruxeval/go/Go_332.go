package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int) []int {
    count := len(nums)
    if count == 0 {
        nums = make([]int, nums[len(nums)-1])
    } else if count%2 == 0 {
        nums = []int{}
    } else {
        nums = nums[count/2:]
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
     { actual: candidate([]int{-6, -2, 1, -3, 0, 1}), expected: []int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
