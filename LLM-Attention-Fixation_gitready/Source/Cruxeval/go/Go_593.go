package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int, n int) []int {
    pos := len(nums) - 1
    for i := -len(nums); i < 0; i++ {
        nums = append(nums[:pos], append([]int{nums[i]}, nums[pos:]...)...)
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
     { actual: candidate([]int{}, 14), expected: []int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
