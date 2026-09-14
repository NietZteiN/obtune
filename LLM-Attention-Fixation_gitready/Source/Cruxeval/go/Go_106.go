package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int) []int {
    count := len(nums)
    for i := 0; i < count; i++ {
        nums = append(nums[:i], append([]int{nums[i]*2}, nums[i:]...)...)
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
     { actual: candidate([]int{2, 8, -2, 9, 3, 3}), expected: []int{4, 4, 4, 4, 4, 4, 2, 8, -2, 9, 3, 3} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
