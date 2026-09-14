package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int, idx int, added int) []int {
    nums = append(nums[:idx], append([]int{added}, nums[idx:]...)...)
    return nums
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{2, 2, 2, 3, 3}, 2, 3), expected: []int{2, 2, 3, 2, 3, 3} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
