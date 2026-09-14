package f_test

import (
    "fmt"
    "testing"
)

func f(nums []int) []int {
    for i := len(nums) - 1; i >= 0; i-- {
        num := nums[0]
        nums = append(nums[:0], nums[1:]...)
        nums = append(nums[:i], append([]int{num}, nums[i:]...)...)
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
     { actual: candidate([]int{0, -5, -4}), expected: []int{-4, -5, 0} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
