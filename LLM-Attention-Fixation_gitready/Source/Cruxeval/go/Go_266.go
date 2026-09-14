package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int) []int {
    for i := len(nums)-1; i >= 0; i-- {
        if nums[i] % 2 == 1 {
            nums = append(nums[:i+1], append([]int{nums[i]}, nums[i+1:]...)...)
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
     { actual: candidate([]int{2, 3, 4, 6, -2}), expected: []int{2, 3, 3, 4, 6, -2} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
