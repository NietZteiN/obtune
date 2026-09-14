package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int) []int {
    count := len(nums) / 2
    for i := 0; i < count; i++ {
        nums = nums[1:]
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
     { actual: candidate([]int{3, 4, 1, 2, 3}), expected: []int{1, 2, 3} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
