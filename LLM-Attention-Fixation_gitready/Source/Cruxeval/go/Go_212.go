package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int) []int {
    for i := 0; i < len(nums)-1; i++ {
        for j := 0; j < len(nums)/2; j++ {
            nums[j], nums[len(nums)-1-j] = nums[len(nums)-1-j], nums[j]
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
     { actual: candidate([]int{1, -9, 7, 2, 6, -3, 3}), expected: []int{1, -9, 7, 2, 6, -3, 3} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
