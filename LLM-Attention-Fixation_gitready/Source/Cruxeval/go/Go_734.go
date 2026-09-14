package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int) []int {
    for i := len(nums) - 1; i >= 0; i-- {
        if nums[i]%2 == 0 {
            nums = append(nums[:i], nums[i+1:]...)
        }
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
     { actual: candidate([]int{5, 3, 3, 7}), expected: []int{5, 3, 3, 7} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
