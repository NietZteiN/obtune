package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int) []int {
    count := len(nums)
    for i := 0; i < count; i++ {
        nums = append(nums, nums[i%2])
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
     { actual: candidate([]int{-1, 0, 0, 1, 1}), expected: []int{-1, 0, 0, 1, 1, -1, 0, -1, 0, -1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
